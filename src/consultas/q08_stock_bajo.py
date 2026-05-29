"""Q8: Productos del stock farmacéutico con menos de 50 unidades disponibles.
Motor: MongoDB — filtro simple con proyección.
"""
from src.db.mongo import get_db


def ejecutar(args=None):
    db = get_db()
    docs = list(db.stock_farmaceutico.find(
        {"unidades": {"$lt": 50}},
        {"nombre": 1, "categoria": 1, "unidades": 1, "proveedor": 1, "vencimiento": 1}
    ).sort("unidades", 1))
    return [{
        "id_producto": d["_id"],
        "nombre": d["nombre"],
        "categoria": d["categoria"],
        "unidades": d["unidades"],
        "proveedor": d["proveedor"],
        "vencimiento": d["vencimiento"].strftime("%Y-%m-%d") if d.get("vencimiento") else "",
    } for d in docs]
