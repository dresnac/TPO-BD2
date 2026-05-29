"""Q9: Consultas de tipo 'Control' con costo inferior a $5.000.
Motor: MongoDB — filtro regex + numérico + $lookup.
"""
from src.db.mongo import get_db


def ejecutar(args=None):
    db = get_db()
    pipeline = [
        {"$match": {"motivo": {"$regex": "Control", "$options": "i"}, "costo": {"$lt": 5000}}},
        {"$lookup": {"from": "pacientes", "localField": "id_paciente",
                     "foreignField": "_id", "as": "paciente"}},
        {"$unwind": "$paciente"},
        {"$lookup": {"from": "veterinarios", "localField": "id_vet",
                     "foreignField": "_id", "as": "vet"}},
        {"$unwind": "$vet"},
        {"$project": {
            "_id": 0,
            "id_consulta": "$_id",
            "paciente": "$paciente.nombre",
            "especie": "$paciente.especie",
            "veterinario": {"$concat": ["$vet.nombre", " ", "$vet.apellido"]},
            "fecha": {"$dateToString": {"format": "%Y-%m-%d", "date": "$fecha"}},
            "motivo": 1, "costo": 1,
        }},
        {"$sort": {"costo": 1}},
    ]
    return list(db.consultas.aggregate(pipeline))
