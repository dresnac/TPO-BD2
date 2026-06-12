"""Q1: Pacientes activos junto con TODOS los datos de su propietario.
Motor: Neo4j (traversal DUEÑO_DE) + MongoDB (enriquecimiento completo).
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
        # Enriquecer con datos del paciente desde MongoDB
        pac = db.pacientes.find_one({"_id": row["id_paciente"]}, {"raza": 1, "fecha_nac": 1})
        if pac:
            row["raza"] = pac.get("raza", "")
            fn = pac.get("fecha_nac")
            row["fecha_nac"] = fn.strftime("%Y-%m-%d") if fn else ""

        # Enriquecer con TODOS los datos del propietario desde MongoDB
        prop = db.propietarios.find_one({"_id": row["id_propietario"]})
        if prop:
            row["dni"] = prop.get("dni", "")
            row["email"] = prop.get("email", "")
            row["telefono"] = prop.get("telefono", "")
            row["provincia"] = prop.get("provincia", "")
    return rows
