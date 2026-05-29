"""Q11: Ingresos totales por veterinario en el mes calendario actual (consultas + cirugías).
Motor: MongoDB — $unionWith consultas+cirugías, $match mes actual, $group por id_vet con $sum costo.
"""
from datetime import datetime
from src.db.mongo import get_db


def ejecutar(args=None):
    db = get_db()
    now = datetime.now()
    inicio_mes = datetime(now.year, now.month, 1)

    pipeline = [
        {"$match": {"fecha": {"$gte": inicio_mes}}},
        {"$project": {"id_vet": 1, "costo": 1, "origen": {"$literal": "consulta"}}},
        {"$unionWith": {
            "coll": "cirugias",
            "pipeline": [
                {"$match": {"fecha": {"$gte": inicio_mes}}},
                {"$project": {"id_vet": 1, "costo": 1, "origen": {"$literal": "cirugia"}}}
            ]
        }},
        {"$group": {
            "_id": "$id_vet",
            "total_ingresos": {"$sum": "$costo"},
            "total_actos": {"$sum": 1}
        }},
        {"$lookup": {"from": "veterinarios", "localField": "_id",
                     "foreignField": "_id", "as": "vet"}},
        {"$unwind": "$vet"},
        {"$project": {
            "_id": 0,
            "id_vet": "$_id",
            "veterinario": {"$concat": ["$vet.nombre", " ", "$vet.apellido"]},
            "especialidad": "$vet.especialidad",
            "sucursal": "$vet.sucursal",
            "total_actos": 1,
            "total_ingresos": 1
        }},
        {"$sort": {"total_ingresos": -1}},
    ]
    return list(db.consultas.aggregate(pipeline))
