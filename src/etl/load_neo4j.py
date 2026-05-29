"""Construye el grafo Neo4j a partir de los datos ya cargados en MongoDB."""
from src.db.mongo import get_db
from src.db.neo import run as neo_run


def _d(dt):
    return dt.strftime("%Y-%m-%d") if dt else None


def load_all():
    db = get_db()

    neo_run("MATCH (n) DETACH DELETE n")

    for stmt in [
        "CREATE CONSTRAINT propietario_id IF NOT EXISTS FOR (p:Propietario) REQUIRE p.id IS UNIQUE",
        "CREATE CONSTRAINT paciente_id    IF NOT EXISTS FOR (p:Paciente)    REQUIRE p.id IS UNIQUE",
        "CREATE CONSTRAINT vet_id         IF NOT EXISTS FOR (v:Veterinario) REQUIRE v.id IS UNIQUE",
        "CREATE CONSTRAINT sucursal_nom   IF NOT EXISTS FOR (s:Sucursal)    REQUIRE s.nombre IS UNIQUE",
        "CREATE CONSTRAINT consulta_id    IF NOT EXISTS FOR (c:Consulta)    REQUIRE c.id IS UNIQUE",
        "CREATE CONSTRAINT vacuna_id      IF NOT EXISTS FOR (v:Vacuna)      REQUIRE v.id IS UNIQUE",
        "CREATE CONSTRAINT cirugia_id     IF NOT EXISTS FOR (c:Cirugia)     REQUIRE c.id IS UNIQUE",
    ]:
        neo_run(stmt)

    # Propietarios
    for doc in db.propietarios.find():
        neo_run(
            "CREATE (:Propietario {id:$id, nombre:$nombre, apellido:$apellido, "
            "ciudad:$ciudad, provincia:$provincia, activo:$activo})",
            id=doc["_id"], nombre=doc["nombre"], apellido=doc["apellido"],
            ciudad=doc["ciudad"], provincia=doc["provincia"], activo=doc["activo"]
        )
    print(f"  :Propietario  : {db.propietarios.count_documents({})}")

    # Veterinarios + Sucursales
    sucursales = set()
    for doc in db.veterinarios.find():
        if doc["sucursal"] not in sucursales:
            neo_run("MERGE (:Sucursal {nombre:$n})", n=doc["sucursal"])
            sucursales.add(doc["sucursal"])
        neo_run(
            "CREATE (:Veterinario {id:$id, nombre:$nombre, apellido:$apellido, "
            "especialidad:$esp, activo:$activo})",
            id=doc["_id"], nombre=doc["nombre"], apellido=doc["apellido"],
            esp=doc["especialidad"], activo=doc["activo"]
        )
        neo_run(
            "MATCH (v:Veterinario {id:$v}), (s:Sucursal {nombre:$s}) CREATE (v)-[:TRABAJA_EN]->(s)",
            v=doc["_id"], s=doc["sucursal"]
        )
    print(f"  :Veterinario  : {db.veterinarios.count_documents({})}")
    print(f"  :Sucursal     : {len(sucursales)}")

    # Pacientes + DUEÑO_DE
    for doc in db.pacientes.find():
        neo_run(
            "CREATE (:Paciente {id:$id, nombre:$nombre, especie:$especie, activo:$activo})",
            id=doc["_id"], nombre=doc["nombre"], especie=doc["especie"], activo=doc["activo"]
        )
        neo_run(
            "MATCH (pr:Propietario {id:$pid}), (p:Paciente {id:$pac}) CREATE (pr)-[:DUEÑO_DE]->(p)",
            pid=doc["id_propietario"], pac=doc["_id"]
        )
    print(f"  :Paciente     : {db.pacientes.count_documents({})}")

    # Consultas + ATENDIDO_EN + REALIZADA_POR
    for doc in db.consultas.find():
        neo_run(
            "CREATE (:Consulta {id:$id, fecha:$fecha, motivo:$motivo, "
            "diagnostico:$diag, costo:$costo, estado:$estado})",
            id=doc["_id"], fecha=_d(doc["fecha"]), motivo=doc["motivo"],
            diag=doc["diagnostico"], costo=doc["costo"], estado=doc["estado"]
        )
        neo_run(
            "MATCH (p:Paciente {id:$pac}), (c:Consulta {id:$con}) "
            "CREATE (p)-[:ATENDIDO_EN {fecha:$fecha, costo:$costo, estado:$estado}]->(c)",
            pac=doc["id_paciente"], con=doc["_id"],
            fecha=_d(doc["fecha"]), costo=doc["costo"], estado=doc["estado"]
        )
        neo_run(
            "MATCH (c:Consulta {id:$con}), (v:Veterinario {id:$vet}) CREATE (c)-[:REALIZADA_POR]->(v)",
            con=doc["_id"], vet=doc["id_vet"]
        )
    print(f"  :Consulta     : {db.consultas.count_documents({})}")

    # Vacunaciones + RECIBIO + APLICADA_POR
    for doc in db.vacunaciones.find():
        neo_run(
            "CREATE (:Vacuna {id:$id, nombre:$nombre, fecha_aplicacion:$fa, proxima_dosis:$pd})",
            id=doc["_id"], nombre=doc["nombre_vacuna"],
            fa=_d(doc["fecha_aplicacion"]), pd=_d(doc["proxima_dosis"])
        )
        neo_run(
            "MATCH (p:Paciente {id:$pac}), (v:Vacuna {id:$vac}) "
            "CREATE (p)-[:RECIBIO {fecha_aplicacion:$fa, proxima_dosis:$pd}]->(v)",
            pac=doc["id_paciente"], vac=doc["_id"],
            fa=_d(doc["fecha_aplicacion"]), pd=_d(doc["proxima_dosis"])
        )
        neo_run(
            "MATCH (va:Vacuna {id:$vac}), (vet:Veterinario {id:$vet}) CREATE (va)-[:APLICADA_POR]->(vet)",
            vac=doc["_id"], vet=doc["id_vet"]
        )
    print(f"  :Vacuna       : {db.vacunaciones.count_documents({})}")

    # Cirugias + OPERADO_EN + REALIZADA_POR
    for doc in db.cirugias.find():
        neo_run(
            "CREATE (:Cirugia {id:$id, fecha:$fecha, tipo:$tipo, costo:$costo, estado:$estado})",
            id=doc["_id"], fecha=_d(doc["fecha"]),
            tipo=doc["tipo"], costo=doc["costo"], estado=doc["estado"]
        )
        neo_run(
            "MATCH (p:Paciente {id:$pac}), (c:Cirugia {id:$cir}) "
            "CREATE (p)-[:OPERADO_EN {fecha:$fecha, costo:$costo, estado:$estado}]->(c)",
            pac=doc["id_paciente"], cir=doc["_id"],
            fecha=_d(doc["fecha"]), costo=doc["costo"], estado=doc["estado"]
        )
        neo_run(
            "MATCH (c:Cirugia {id:$cir}), (v:Veterinario {id:$vet}) CREATE (c)-[:REALIZADA_POR]->(v)",
            cir=doc["_id"], vet=doc["id_vet"]
        )
    print(f"  :Cirugia      : {db.cirugias.count_documents({})}")
