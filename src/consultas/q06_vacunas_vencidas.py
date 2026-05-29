"""Q6: Pacientes con vacunas vencidas (proxima_dosis anterior a la fecha actual).
Motor: MongoDB — $match por fecha + $lookup a pacientes y propietarios.
"""
from datetime import datetime
from src.db.mongo import get_db


def ejecutar(args=None):
    db = get_db()
    pipeline = [
        {"$match": {"proxima_dosis": {"$lt": datetime.now()}}},
        {"$lookup": {"from": "pacientes", "localField": "id_paciente",
                     "foreignField": "_id", "as": "paciente"}},
        {"$unwind": "$paciente"},
        {"$lookup": {"from": "propietarios", "localField": "paciente.id_propietario",
                     "foreignField": "_id", "as": "propietario"}},
        {"$unwind": "$propietario"},
        {"$project": {
            "_id": 0,
            "id_vacuna": "$_id",
            "paciente": "$paciente.nombre",
            "especie": "$paciente.especie",
            "propietario": {"$concat": ["$propietario.nombre", " ", "$propietario.apellido"]},
            "telefono": "$propietario.telefono",
            "vacuna": "$nombre_vacuna",
            "fecha_aplicacion": {"$dateToString": {"format": "%Y-%m-%d", "date": "$fecha_aplicacion"}},
            "proxima_dosis": {"$dateToString": {"format": "%Y-%m-%d", "date": "$proxima_dosis"}},
        }},
        {"$sort": {"proxima_dosis": 1}},
    ]
    return list(db.vacunaciones.aggregate(pipeline))
