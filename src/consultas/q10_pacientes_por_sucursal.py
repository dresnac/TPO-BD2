"""Q10: Pacientes atendidos en una sucursal específica (vía veterinario que trabaja allí).
Motor: Neo4j — traversal de 3 saltos: Sucursal←TRABAJA_EN←Vet←REALIZADA_POR←Consulta←ATENDIDO_EN←Paciente.
"""
from src.db.neo import run as neo_run


def ejecutar(args=None):
    sucursal = args if isinstance(args, str) else input("Sucursal (ej. Palermo): ").strip()
    results = neo_run(
        "MATCH (s:Sucursal {nombre: $suc})<-[:TRABAJA_EN]-(v:Veterinario)"
        "<-[:REALIZADA_POR]-(c:Consulta)<-[:ATENDIDO_EN]-(p:Paciente) "
        "RETURN DISTINCT p.id AS id_paciente, p.nombre AS paciente, p.especie AS especie, "
        "v.nombre + ' ' + v.apellido AS atendido_por "
        "ORDER BY p.nombre",
        suc=sucursal
    )
    return [dict(r) for r in results]
