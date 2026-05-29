"""Q5: Veterinarios activos y cantidad de consultas realizadas en los últimos 60 días.
Motor: MongoDB — $match por fecha + $group + $lookup con filtro activo.
"""
from datetime import datetime, timedelta
from src.db.mongo import get_db


def ejecutar(args=None):
    db = get_db()
    hace_60 = datetime.now() - timedelta(days=60)
    pipeline = [
        {"$match": {"fecha": {"$gte": hace_60}}},
        {"$group": {"_id": "$id_vet", "total_consultas": {"$sum": 1}}},
        {"$lookup": {"from": "veterinarios", "localField": "_id",
                     "foreignField": "_id", "as": "vet"}},
        {"$unwind": "$vet"},
        {"$match": {"vet.activo": True}},
        {"$project": {
            "_id": 0,
            "id_vet": "$_id",
            "veterinario": {"$concat": ["$vet.nombre", " ", "$vet.apellido"]},
            "especialidad": "$vet.especialidad",
            "sucursal": "$vet.sucursal",
            "total_consultas": 1
        }},
        {"$sort": {"total_consultas": -1}},
    ]
    return list(db.consultas.aggregate(pipeline))
