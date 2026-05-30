"""Q4: Propietarios con más de un paciente registrado.
Motor: Neo4j — conteo de relaciones DUEÑO_DE.
"""
from src.db.neo import run as neo_run


def ejecutar(args=None):
    results = neo_run(
        "MATCH (pr:Propietario)-[:DUEÑO_DE]->(p:Paciente) "
        "WITH pr, count(p) AS total "
        "WHERE total > 1 "
        "RETURN pr.id AS id_propietario, "
        "pr.nombre + ' ' + pr.apellido AS propietario, "
        "pr.ciudad AS ciudad, total AS total_pacientes "
        "ORDER BY total DESC, pr.apellido"
    )
    return [dict(r) for r in results]
