"""Q12: Propietarios sin consultas registradas en el último año.
Motor: Neo4j (filtrado por negación del camino DUEÑO_DE -> ATENDIDO_EN con condición de fecha) 
"""

from datetime import datetime, timedelta
from src.db.neo import run as neo_run

def ejecutar(args=None):
    hace_un_anio = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    results = neo_run(
       "MATCH (pr:Propietario) "
        "WHERE NOT EXISTS { "
        "   MATCH (pr)-[:DUEÑO_DE]->(:Paciente)-[:ATENDIDO_EN]->(c:Consulta) "
        "   WHERE c.fecha >= $fecha_limite "
        "} "
        "RETURN pr.id AS id_propietario, "
        "       pr.nombre + ' ' + pr.apellido AS propietario, "
        "       pr.ciudad AS ciudad "
        "ORDER BY pr.apellido, pr.nombre",
        fecha_limite=hace_un_anio
    )
    
    return [dict(r) for r in results]