"""Q2: Consultas en estado 'Seguimiento' con datos del veterinario y costo.
Motor: MongoDB — filtro simple + $lookup.
"""
from src.db.mongo import get_db


def ejecutar(args=None):
    db = get_db()
    pipeline = [
        {"$match": {"estado": "Seguimiento"}},
        {"$lookup": {"from": "veterinarios", "localField": "id_vet",
                     "foreignField": "_id", "as": "vet"}},
        {"$unwind": "$vet"},
        {"$lookup": {"from": "pacientes", "localField": "id_paciente",
                     "foreignField": "_id", "as": "paciente"}},
        {"$unwind": "$paciente"},
        {"$project": {
            "_id": 0,
            "id_consulta": "$_id",
            "paciente": "$paciente.nombre",
            "veterinario": {"$concat": ["$vet.nombre", " ", "$vet.apellido"]},
            "especialidad": "$vet.especialidad",
            "fecha": {"$dateToString": {"format": "%Y-%m-%d", "date": "$fecha"}},
            "motivo": 1, "diagnostico": 1, "costo": 1, "estado": 1
        }},
        {"$sort": {"fecha": -1}},
    ]
    return list(db.consultas.aggregate(pipeline))
