"""Módulo para el ABM operativo completo de Propietarios (MongoDB + Neo4j).
Cumple con: Alta , Modificación de datos y Baja Lógica.
"""

from datetime import datetime
from pymongo import DESCENDING
from src.db.mongo import get_db
from src.db.neo import run as neo_run

# =====================================================================
# ALTA DE PROPIETARIOS Y SUS PACIENTES
# =====================================================================

def alta(datos_entrada):
    """Registra un nuevo propietario junto con una lista opcional de sus pacientes.
    Maneja IDs autoincrementales dinámicos tanto en MongoDB como en Neo4j.
    
    Estructura esperada de datos_entrada:
    {
        "nombre": "Juan",
        "apellido": "Pérez",
        "dni": "12345678",
        "email": "juan@email.com",
        "telefono": "11223344",
        "ciudad": "Palermo",
        "provincia": "Buenos Aires",
        "pacientes": [  # Lista opcional
            {
                "nombre": "Firulais",
                "especie": "Canina",
                "raza": "Labrador",
                "fecha_nac": "2022-03-15"
            }
        ]
    }
    """
    db = get_db()
    pacientes_ingresar = datos_entrada.get("pacientes", [])

    # 1. Autocalcular el ID autoincremental del Propietario
    ultimo_propietario = db.propietarios.find_one({}, sort=[("_id", DESCENDING)])
    id_propietario = (int(ultimo_propietario["_id"]) + 1) if ultimo_propietario else 1

    # Construir documento del propietario para MongoDB
    doc_propietario = {
        "_id": id_propietario,
        "nombre": datos_entrada.get("nombre"),
        "apellido": datos_entrada.get("apellido"),
        "dni": datos_entrada.get("dni"),
        "email": datos_entrada.get("email"),
        "telefono": datos_entrada.get("telefono"),
        "ciudad": datos_entrada.get("ciudad"),
        "provincia": datos_entrada.get("provincia"),
        "activo": True
    }

    # 2. Procesar y autocalcular IDs de los Pacientes
    docs_pacientes_mongo = []
    nodos_pacientes_neo = []

    if pacientes_ingresar:
        # Obtener el último ID base de pacientes para el autoincremento secuencial
        ultimo_paciente = db.pacientes.find_one({}, sort=[("_id", DESCENDING)])
        id_paciente_actual = (int(ultimo_paciente["_id"]) + 1) if ultimo_paciente else 1

        for p in pacientes_ingresar:
            # Procesar fecha de nacimiento
            fecha_str = p.get("fecha_nac")
            fecha_dt = None
            if fecha_str:
                try:
                    fecha_dt = datetime.strptime(fecha_str.strip(), "%Y-%m-%d")
                except ValueError:
                    fecha_dt = None

            # Documento para MongoDB
            paciente_mongo = {
                "_id": id_paciente_actual,
                "nombre": p.get("nombre"),
                "especie": p.get("especie"),
                "raza": p.get("raza"),
                "fecha_nac": fecha_dt,
                "id_propietario": id_propietario,
                "activo": True
            }
            docs_pacientes_mongo.append(paciente_mongo)

            # Diccionario mapeado para la query de Neo4j
            paciente_neo = {
                "id": id_paciente_actual,
                "nombre": p.get("nombre"),
                "especie": p.get("especie"),
                "activo": True
            }
            nodos_pacientes_neo.append(paciente_neo)

            id_paciente_actual += 1

    # 3. Persistencia en MONGODB
    try:
        # Insertar propietario
        db.propietarios.insert_one(doc_propietario)
        # Insertar pacientes si existen
        if docs_pacientes_mongo:
            db.pacientes.insert_many(docs_pacientes_mongo)
    except Exception as e:
        return {
            "status": "error",
            "mensaje": "Error de concurrencia o duplicación al escribir en MongoDB.",
            "error": str(e)
        }

    # 4. Persistencia en NEO4J
    try:
        # Crear nodo Propietario
        query_prop_neo = """
        CREATE (:Propietario {
            id: $id, 
            nombre: $nombre, 
            apellido: $apellido, 
            ciudad: $ciudad, 
            provincia: $provincia, 
            activo: $activo
        })
        """
        neo_run(
            query_prop_neo,
            id=id_propietario,
            nombre=doc_propietario["nombre"],
            apellido=doc_propietario["apellido"],
            ciudad=doc_propietario["ciudad"],
            provincia=doc_propietario["provincia"],
            activo=True
        )

        # Crear nodos Pacientes y sus relaciones [:DUEÑO_DE]
        # Crear nodos Pacientes y sus relaciones [:DUEÑO_DE]
        for p_neo in nodos_pacientes_neo:
            query_pac_neo = """
            CREATE (p:Paciente {
                id: $id, 
                nombre: $nombre, 
                especie: $especie, 
                activo: $activo
            })
            WITH p
            MATCH (pr:Propietario {id: $pid})
            CREATE (pr)-[:DUEÑO_DE]->(p)
            """
            neo_run(
                query_pac_neo,
                id=p_neo["id"],
                nombre=p_neo["nombre"],
                especie=p_neo["especie"],
                activo=p_neo["activo"],
                pid=id_propietario
            )
    except Exception as e:
        return {
            "status": "error",
            "mensaje": f"El propietario se creó en MongoDB pero falló la sincronización en Neo4j.",
            "error": str(e)
        }

    return {
        "status": "success",
        "propietario_id": id_propietario,
        "pacientes_registrados": [p["_id"] for p in docs_pacientes_mongo],
        "mensaje": f"Propietario con id {id_propietario} y sus {len(docs_pacientes_mongo)} paciente(s) creados con éxito."
    }


# =====================================================================
# BAJA LÓGICA DE PROPIETARIOS
# =====================================================================

def baja_logica(id_propietario):
    id_propietario = int(id_propietario)

    # 1. Validación en Neo4j: evitar baja si tiene animales activos
    query_validacion = """
    MATCH (pr:Propietario {id: $id})-[:DUEÑO_DE]->(p:Paciente)
    WHERE p.activo = true
    RETURN count(p) AS pacientes_activos
    """
    res_validacion = neo_run(query_validacion, id=id_propietario)
    pacientes_activos = res_validacion[0]["pacientes_activos"] if res_validacion else 0

    if pacientes_activos > 0:
        return {
            "status": "error",
            "mensaje": f"No se puede dar de baja al propietario. Tiene {pacientes_activos} paciente(s) activo(s) a su cargo.",
        }

    # 2. Baja lógica en MongoDB
    db = get_db()
    resultado_mongo = db.propietarios.update_one(
        {"_id": id_propietario},
        {"$set": {"activo": False}},
    )

    if resultado_mongo.matched_count == 0:
        return {
            "status": "error",
            "mensaje": f"El propietario con ID {id_propietario} no existe en MongoDB.",
        }

    # 3. Baja lógica en Neo4j
    query_baja_neo = """
    MATCH (pr:Propietario {id: $id})
    SET pr.activo = false
    RETURN pr
    """
    neo_run(query_baja_neo, id=id_propietario)

    return {
        "status": "success",
        "mensaje": f"Propietario {id_propietario} dado de baja lógicamente con éxito.",
    }


# =====================================================================
# MODIFICACIÓN DE DATOS
# =====================================================================

def modificacion(id_propietario, nuevos_datos):
    id_propietario = int(id_propietario)
    db = get_db()

    nuevos_datos.pop("_id", None)
    nuevos_datos.pop("id", None)
    nuevos_datos.pop("pacientes", None)  # El ABM de datos del propietario no modifica el array de mascotas directamente

    if not nuevos_datos:
        return {
            "status": "error",
            "mensaje": "No se proporcionaron datos para actualizar.",
        }

    # 1. Actualización en MongoDB
    resultado_mongo = db.propietarios.update_one(
        {"_id": id_propietario},
        {"$set": nuevos_datos},
    )

    if resultado_mongo.matched_count == 0:
        return {
            "status": "error",
            "mensaje": f"El propietario con ID {id_propietario} no existe en el sistema.",
        }

    # 2. Actualización en Neo4j (Filtrando las propiedades que corresponden al nodo :Propietario)
    campos_neo = ["nombre", "apellido", "ciudad", "provincia", "activo"]
    datos_para_neo = {k: v for k, v in nuevos_datos.items() if k in campos_neo}

    if datos_para_neo:
        set_clauses = ", ".join([f"pr.{k} = ${k}" for k in datos_para_neo])
        query_neo = f"""
        MATCH (pr:Propietario {{id: $id}})
        SET {set_clauses}
        RETURN pr
        """
        neo_run(query_neo, id=id_propietario, **datos_para_neo)

    return {
        "status": "success",
        "mensaje": f"Propietario {id_propietario} actualizado correctamente en ambas bases de datos.",
    }