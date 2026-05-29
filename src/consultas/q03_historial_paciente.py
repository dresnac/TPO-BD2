"""Q3: Historial clínico completo de un paciente (consultas + vacunaciones + cirugías).
Motor: MongoDB — $unionWith x2 sobre las tres colecciones, ordenado por fecha desc.
"""
from src.db.mongo import get_db


def ejecutar(args=None):
    db = get_db()
    id_paciente = args if isinstance(args, str) else input("ID del paciente (ej. P001): ").strip()

    pipeline = [
        {"$match": {"id_paciente": id_paciente}},
        {"$project": {
            "fecha": 1, "tipo": {"$literal": "Consulta"},
            "detalle": "$motivo", "resultado": "$diagnostico",
            "costo": 1, "id_vet": 1
        }},
        {"$unionWith": {
            "coll": "vacunaciones",
            "pipeline": [
                {"$match": {"id_paciente": id_paciente}},
                {"$project": {
                    "fecha": "$fecha_aplicacion", "tipo": {"$literal": "Vacunación"},
                    "detalle": "$nombre_vacuna", "resultado": {"$literal": "—"},
                    "costo": {"$literal": 0}, "id_vet": 1
                }}
            ]
        }},
        {"$unionWith": {
            "coll": "cirugias",
            "pipeline": [
                {"$match": {"id_paciente": id_paciente}},
                {"$project": {
                    "fecha": 1, "tipo": {"$literal": "Cirugía"},
                    "detalle": "$tipo", "resultado": "$estado",
                    "costo": 1, "id_vet": 1
                }}
            ]
        }},
        {"$lookup": {"from": "veterinarios", "localField": "id_vet",
                     "foreignField": "_id", "as": "vet"}},
        {"$unwind": {"path": "$vet", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "_id": 0,
            "fecha": {"$dateToString": {"format": "%Y-%m-%d", "date": "$fecha"}},
            "tipo": 1, "detalle": 1, "resultado": 1, "costo": 1,
            "veterinario": {"$concat": ["$vet.nombre", " ", "$vet.apellido"]}
        }},
        {"$sort": {"fecha": -1}},
    ]
    return list(db.consultas.aggregate(pipeline))
