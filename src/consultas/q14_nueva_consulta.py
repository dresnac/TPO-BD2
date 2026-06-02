"""Q14: Registro de nueva consulta médica con validación de paciente y veterinario existentes.
"""

from datetime import datetime
from pymongo import DESCENDING
from src.db.mongo import get_db
from src.db.neo import run as neo_run

def ejecutar(datos_consulta):
    """Registra una nueva consulta médica validando la existencia y actividad
    del paciente y del veterinario implicados.

    datos_consulta: dict con las llaves 'id_paciente', 'id_vet', 'fecha',
                    'motivo', 'diagnostico', 'costo', 'estado'.
    """
    db = get_db()

    id_paciente = int(datos_consulta.get("id_paciente"))
    id_vet = int(datos_consulta.get("id_vet"))

    query_validacion = """
    OPTIONAL MATCH (p:Paciente {id: $id_paciente})
    OPTIONAL MATCH (v:Veterinario {id: $id_vet})
    RETURN p IS NOT NULL AND p.activo = true AS paciente_ok,
           v IS NOT NULL AND v.activo = true AS vet_ok
    """

    res_val = neo_run(
        query_validacion,
        id_paciente=id_paciente,
        id_vet=id_vet,
    )

    if not res_val:
        return {
            "status": "error",
            "mensaje": "Error crítico al ejecutar las validaciones en el sistema.",
        }

    validacion = res_val[0]

    if not validacion["paciente_ok"]:
        return {
            "status": "error",
            "mensaje": f"El paciente con ID {id_paciente} no existe o no se encuentra activo.",
        }

    if not validacion["vet_ok"]:
        return {
            "status": "error",
            "mensaje": f"El veterinario con ID {id_vet} no existe o no se encuentra activo.",
        }

    # Generación automática del ID de consulta
    ultima_consulta = db.consultas.find_one(
        {},
        sort=[("_id", DESCENDING)]
    )

    if ultima_consulta:
        id_consulta = int(ultima_consulta["_id"]) + 1
    else:
        id_consulta = 1

    fecha_consulta = datos_consulta.get("fecha")

    if isinstance(fecha_consulta, str):
        fecha_dt = datetime.strptime(
            fecha_consulta.strip(),
            "%Y-%m-%d"
        )
    else:
        fecha_dt = fecha_consulta or datetime.now()

    fecha_str = fecha_dt.strftime("%Y-%m-%d")

    doc_mongo = {
        "_id": id_consulta,
        "id_paciente": id_paciente,
        "id_vet": id_vet,
        "fecha": fecha_dt,
        "motivo": datos_consulta.get("motivo", ""),
        "diagnostico": datos_consulta.get("diagnostico", ""),
        "costo": float(datos_consulta.get("costo", 0.0)),
        "estado": datos_consulta.get(
            "estado",
            "Completada"
        ),
    }

    try:
        db.consultas.insert_one(doc_mongo)
    except Exception as e:
        return {
            "status": "error",
            "mensaje": f"Error de concurrencia al asignar el ID {id_consulta}. Intente nuevamente.",
            "error": str(e),
        }

    query_neo = """
    CREATE (c:Consulta {
        id: $id,
        fecha: $fecha,
        motivo: $motivo,
        diagnostico: $diagnostico,
        costo: $costo,
        estado: $estado
    })
    WITH c
    MATCH (p:Paciente {id: $id_paciente})
    CREATE (p)-[:ATENDIDO_EN {
        fecha: $fecha,
        costo: $costo,
        estado: $estado
    }]->(c)
    WITH c
    MATCH (v:Veterinario {id: $id_vet})
    CREATE (c)-[:REALIZADA_POR]->(v)
    RETURN c
    """

    neo_run(
        query_neo,
        id=id_consulta,
        fecha=fecha_str,
        motivo=doc_mongo["motivo"],
        diagnostico=doc_mongo["diagnostico"],
        costo=doc_mongo["costo"],
        estado=doc_mongo["estado"],
        id_paciente=id_paciente,
        id_vet=id_vet,
    )

    return {
        "status": "success",
        "id_assigned": id_consulta,
        "mensaje": f"Consulta {id_consulta} registrada exitosamente para el paciente {id_paciente}.",
    }