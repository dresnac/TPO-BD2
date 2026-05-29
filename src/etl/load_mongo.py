"""Carga idempotente de todos los CSVs en MongoDB."""
import csv
import os
from datetime import datetime
from pymongo import ASCENDING
from src.db.mongo import get_db

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DS = os.path.join(_ROOT, "datasets_vetsalud")
_DATA = os.path.join(_ROOT, "data")
_EXTRAS = os.path.join(_DATA, "extras")


def _csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _date(s):
    return datetime.strptime(s.strip(), "%Y-%m-%d") if s and s.strip() else None


def _bool(s):
    return s.strip().lower() in ("true", "1", "yes")


def _int(s):
    return int(s.strip()) if s and s.strip() else 0


def _float(s):
    return float(s.strip()) if s and s.strip() else 0.0


def load_all():
    db = get_db()

    # propietarios
    db.propietarios.drop()
    rows = _csv(os.path.join(_DS, "propietarios.csv")) + _csv(os.path.join(_EXTRAS, "propietarios_extras.csv"))
    db.propietarios.insert_many([{
        "_id": r["id_propietario"], "nombre": r["nombre"], "apellido": r["apellido"],
        "dni": r["dni"], "email": r["email"], "telefono": r["telefono"],
        "ciudad": r["ciudad"], "provincia": r["provincia"], "activo": True
    } for r in rows])
    db.propietarios.create_index([("ciudad", ASCENDING)])
    print(f"  propietarios : {len(rows)}")

    # pacientes
    db.pacientes.drop()
    rows = _csv(os.path.join(_DS, "pacientes.csv")) + _csv(os.path.join(_EXTRAS, "pacientes_extras.csv"))
    db.pacientes.insert_many([{
        "_id": r["id_paciente"], "nombre": r["nombre"], "especie": r["especie"],
        "raza": r["raza"], "fecha_nac": _date(r["fecha_nac"]),
        "id_propietario": r["id_propietario"], "activo": _bool(r["activo"])
    } for r in rows])
    db.pacientes.create_index([("id_propietario", ASCENDING)])
    db.pacientes.create_index([("activo", ASCENDING)])
    print(f"  pacientes    : {len(rows)}")

    # veterinarios
    db.veterinarios.drop()
    rows = _csv(os.path.join(_DS, "veterinarios.csv")) + _csv(os.path.join(_EXTRAS, "veterinarios_extras.csv"))
    db.veterinarios.insert_many([{
        "_id": r["id_vet"], "nombre": r["nombre"], "apellido": r["apellido"],
        "matricula": r["matricula"], "especialidad": r["especialidad"],
        "sucursal": r["sucursal"], "activo": _bool(r["activo"])
    } for r in rows])
    db.veterinarios.create_index([("activo", ASCENDING)])
    db.veterinarios.create_index([("sucursal", ASCENDING)])
    print(f"  veterinarios : {len(rows)}")

    # consultas
    db.consultas.drop()
    rows = _csv(os.path.join(_DS, "consultas.csv")) + _csv(os.path.join(_EXTRAS, "consultas_extras.csv"))
    db.consultas.insert_many([{
        "_id": r["id_consulta"], "id_paciente": r["id_paciente"], "id_vet": r["id_vet"],
        "fecha": _date(r["fecha"]), "motivo": r["motivo"], "diagnostico": r["diagnostico"],
        "costo": _float(r["costo"]), "estado": r["estado"]
    } for r in rows])
    db.consultas.create_index([("fecha", ASCENDING)])
    db.consultas.create_index([("estado", ASCENDING)])
    db.consultas.create_index([("id_paciente", ASCENDING)])
    db.consultas.create_index([("id_vet", ASCENDING)])
    print(f"  consultas    : {len(rows)}")

    # vacunaciones
    db.vacunaciones.drop()
    rows = _csv(os.path.join(_DS, "vacunaciones.csv")) + _csv(os.path.join(_EXTRAS, "vacunaciones_extras.csv"))
    db.vacunaciones.insert_many([{
        "_id": r["id_vacuna"], "id_paciente": r["id_paciente"], "id_vet": r["id_vet"],
        "fecha_aplicacion": _date(r["fecha_aplicacion"]), "nombre_vacuna": r["nombre_vacuna"],
        "proxima_dosis": _date(r["proxima_dosis"])
    } for r in rows])
    db.vacunaciones.create_index([("proxima_dosis", ASCENDING)])
    db.vacunaciones.create_index([("id_paciente", ASCENDING)])
    print(f"  vacunaciones : {len(rows)}")

    # cirugias
    db.cirugias.drop()
    rows = _csv(os.path.join(_DATA, "cirugias.csv")) + _csv(os.path.join(_EXTRAS, "cirugias_extras.csv"))
    db.cirugias.insert_many([{
        "_id": r["id_cirugia"], "id_paciente": r["id_paciente"], "id_vet": r["id_vet"],
        "fecha": _date(r["fecha"]), "tipo": r["tipo"], "descripcion": r["descripcion"],
        "anestesia": r["anestesia"], "duracion_min": _int(r["duracion_min"]),
        "costo": _float(r["costo"]), "estado": r["estado"],
        "observaciones_post": r.get("observaciones_post", "")
    } for r in rows])
    db.cirugias.create_index([("id_paciente", ASCENDING)])
    db.cirugias.create_index([("id_vet", ASCENDING)])
    db.cirugias.create_index([("fecha", ASCENDING)])
    print(f"  cirugias     : {len(rows)}")

    # stock_farmaceutico
    db.stock_farmaceutico.drop()
    rows = _csv(os.path.join(_DS, "stock_farmaceutico.csv")) + _csv(os.path.join(_EXTRAS, "stock_farmaceutico_extras.csv"))
    db.stock_farmaceutico.insert_many([{
        "_id": r["id_producto"], "nombre": r["nombre"], "categoria": r["categoria"],
        "unidades": _int(r["unidades"]), "precio_unit": _float(r["precio_unit"]),
        "vencimiento": _date(r["vencimiento"]), "proveedor": r["proveedor"]
    } for r in rows])
    db.stock_farmaceutico.create_index([("unidades", ASCENDING)])
    db.stock_farmaceutico.create_index([("categoria", ASCENDING)])
    print(f"  stock        : {len(rows)}")
