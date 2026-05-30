"""Módulo para el ABM operativo completo de Propietarios (MongoDB + Neo4j).
Cumple con: Alta, Modificación de datos y Baja Lógica.
"""

import re
from pymongo import DESCENDING
from src.db.mongo import get_db
from src.db.neo import run as neo_run


# =====================================================================
# ALTA DE PROPIETARIOS
# =====================================================================
def alta(datos_propietario):
    """Registra un nuevo propietario calculando dinámicamente el último ID + 1
    y asegurando su estado activo por defecto.
    """
    db = get_db()

    # 0. Autocalcular el siguiente ID dinámicamente
    ultimo_propietario = db.propietarios.find_one(
        {}, sort=[("_id", DESCENDING)]
    )

    if ultimo_propietario:
        ultimo_id = ultimo_propietario["_id"]

        numeros = re.findall(r"\d+", ultimo_id)
        if numeros:
            ultimo_numero_str = numeros[-1]
            prefijo = ultimo_id.split(ultimo_numero_str)[0]
            siguiente_numero = int(ultimo_numero_str) + 1
            id_propietario = f"{prefijo}{str(siguiente_numero).zfill(len(ultimo_numero_str))}"
        else:
            raise ValueError(
                f"No se pudo determinar el patrón numérico del último ID válido: {ultimo_id}"
            )
    else:
        id_propietario = "PROP-001"

    datos_propietario["_id"] = id_propietario
    datos_propietario["activo"] = True

    # 1. Inserción en MongoDB
    try:
        db.propietarios.insert_one(datos_propietario)
    except Exception as e:
        return {
            "status": "error",
            "mensaje": f"Error de concurrencia al intentar asignar el ID {id_propietario}. Intente nuevamente.",
            "error": str(e),
        }

    # 2. Inserción en Neo4j
    query_neo = """
    MERGE (pr:Propietario {id: $id})
    SET pr.nombre = $nombre,
        pr.apellido = $apellido,
        pr.ciudad = $ciudad,
        pr.activo = true
    RETURN pr
    """
    neo_run(
        query_neo,
        id=id_propietario,
        nombre=datos_propietario.get("nombre"),
        apellido=datos_propietario.get("apellido"),
        ciudad=datos_propietario.get("ciudad"),
    )

    return {
        "status": "success",
        "id_asignado": id_propietario,
        "mensaje": f"Propietario {id_propietario} creado correctamente en ambas bases de datos con estado activo.",
    }


# =====================================================================
# BAJA LÓGICA DE PROPIETARIOS
# =====================================================================
def baja_logica(id_propietario):
    """Realiza la baja lógica de un propietario si no tiene pacientes activos."""
    # 1. Validación en Neo4j
    query_validacion = """
    MATCH (pr:Propietario {id: $id})-[:DUEÑO_DE]->(p:Paciente)
    WHERE p.activo = true
    RETURN count(p) AS pacientes_activos
    """
    res_validacion = neo_run(query_validacion, id=id_propietario)
    pacientes_activos = (
        res_validacion[0]["pacientes_activos"] if res_validacion else 0
    )

    if pacientes_activos > 0:
        return {
            "status": "error",
            "mensaje": f"No se puede dar de baja al propietario. Tiene {pacientes_activos} paciente(s) activo(s) a su cargo.",
        }

    # 2. Baja lógica en MongoDB
    db = get_db()
    resultado_mongo = db.propietarios.update_one(
        {"_id": id_propietario}, {"$set": {"activo": False}}
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
def modificar(id_propietario, nuevos_datos):
    """Actualiza los datos de un propietario en ambas bases de datos."""
    db = get_db()

    nuevos_datos.pop("_id", None)
    nuevos_datos.pop("id", None)

    if not nuevos_datos:
        return {
            "status": "error",
            "mensaje": "No se proporcionaron datos para actualizar.",
        }

    # 1. Actualización en MongoDB
    resultado_mongo = db.propietarios.update_one(
        {"_id": id_propietario}, {"$set": nuevos_datos}
    )

    if resultado_mongo.matched_count == 0:
        return {
            "status": "error",
            "mensaje": f"El propietario con ID {id_propietario} no existe en el sistema.",
        }

    # 2. Actualización en Neo4j
    campos_neo = ["nombre", "apellido", "ciudad", "activo"]
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