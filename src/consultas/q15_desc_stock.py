""" Q15: Actualización masiva del stock: decrementar unidades de un producto tras una
consulta. """

from src.db.mongo import get_db


def descontar_producto_individual(id_producto_limpio, cantidad_a_descontar):
    """Busca un producto por su ID (ya parseado sin prefijo), verifica que

    tenga stock suficiente y le resta la cantidad indicada.

    id_producto_limpio: int o str (ej: 145 o "145")
    cantidad_a_descontar: int (ej: 3)
    """
    if cantidad_a_descontar <= 0:
        return {
            "status": "error",
            "mensaje": "La cantidad a descontar debe ser mayor a cero.",
        }

    db = get_db()

   
    try:
        id_busqueda = int(id_producto_limpio)
    except ValueError:
        id_busqueda = str(id_producto_limpio)

    filtro = {"_id": id_busqueda, "unidades": {"$gte": cantidad_a_descontar}}

    actualizacion = {"$inc": {"unidades": -cantidad_a_descontar}}

    resultado = db.stock_farmaceutico.update_one(filtro, actualizacion)

    if resultado.modified_count == 1:
        return {
            "status": "success",
            "mensaje": f"Se descontaron {cantidad_a_descontar} unidades del producto {id_producto_limpio} con éxito.",
        }

    # Si no se modificó nada --> xq fallo ¿?
    producto_existe = db.stock_farmaceutico.find_one({"_id": id_busqueda})

    if not producto_existe:
        return {
            "status": "error",
            "mensaje": f"El producto con ID {id_producto_limpio} no existe en la base de datos.",
        }
    else:
        stock_actual = producto_existe.get("unidades", 0)
        return {
            "status": "error",
            "mensaje": f"Stock insuficiente para el producto {id_producto_limpio}.",
            "detalles": {
                "stock_disponible": stock_actual,
                "cantidad_solicitada": cantidad_a_descontar,
            },
        }