"""Q7: Top 5 diagnósticos más frecuentes en todas las consultas.
Motor: MongoDB — $group + $sort + $limit.
"""
from src.db.mongo import get_db


def ejecutar(args=None):
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$diagnostico", "frecuencia": {"$sum": 1}}},
        {"$sort": {"frecuencia": -1}},
        {"$limit": 5},
        {"$project": {"_id": 0, "diagnostico": "$_id", "frecuencia": 1}},
    ]
    return list(db.consultas.aggregate(pipeline))
