"""Q1: Pacientes activos junto con los datos de su propietario.
Motor: Neo4j (traversal DUEÑO_DE) + MongoDB (enriquecimiento con raza y fecha_nac).
"""
from src.db.neo import run as neo_run
from src.db.mongo import get_db


def ejecutar(args=None):
    results = neo_run(
        "MATCH (pr:Propietario)-[:DUEÑO_DE]->(p:Paciente {activo: true}) "
        "RETURN pr.id AS id_propietario, "
        "pr.nombre + ' ' + pr.apellido AS propietario, "
        "pr.ciudad AS ciudad, "
        "p.id AS id_paciente, p.nombre AS paciente, p.especie AS especie "
        "ORDER BY pr.apellido, p.nombre"
    )
    rows = [dict(r) for r in results]
    db = get_db()
    for row in rows:
        doc = db.pacientes.find_one({"_id": row["id_paciente"]}, {"raza": 1, "fecha_nac": 1})
        if doc:
            row["raza"] = doc.get("raza", "")
            fn = doc.get("fecha_nac")
            row["fecha_nac"] = fn.strftime("%Y-%m-%d") if fn else ""
    return rows
