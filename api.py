from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import RedirectResponse
from src.consultas import (
    q01_pacientes_activos,
    q02_consultas_abiertas,
    q03_historial_paciente,
    q04_propietarios_multi_paciente,
    q05_vets_consultas_60d,
    q06_vacunas_vencidas,
    q07_top5_diagnosticos,
    q08_stock_bajo,
    q09_consultas_control,
    q10_pacientes_por_sucursal,
    q11_ingresos_por_vet
)

app = FastAPI(
    title="VetSalud S.A. - API de Persistencia Políglota",
    description="Backend para la gestión de clínica veterinaria utilizando persistencia documental en MongoDB y persistencia de grafos en Neo4j.",
    version="1.0.0"
)

@app.get("/", include_in_schema=False)
def index():
    # Redirige automáticamente a la documentación Swagger interactiva
    return RedirectResponse(url="/docs")

@app.get(
    "/consultas/pacientes-activos", 
    summary="[Q01] Pacientes activos junto con todos sus datos de propietario",
    description="Motor: Neo4j (traversal de dueños de pacientes activos) + MongoDB (información del paciente).",
    tags=["Consultas"]
)
def get_pacientes_activos():
    try:
        return q01_pacientes_activos.ejecutar()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al ejecutar consulta: {str(e)}")

@app.get(
    "/consultas/consultas-seguimiento", 
    summary="[Q02] Consultas médicas abiertas en estado 'Seguimiento'",
    description="Motor: MongoDB (filtro simple + agregación $lookup para enriquecer veterinario y paciente).",
    tags=["Consultas"]
)
def get_consultas_seguimiento():
    try:
        return q02_consultas_abiertas.ejecutar()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al ejecutar consulta: {str(e)}")

@app.get(
    "/consultas/historial-clinico", 
    summary="[Q03] Historial clínico completo de un paciente",
    description="Motor: MongoDB (unión de consultas, vacunaciones y cirugías mediante $unionWith).",
    tags=["Consultas"]
)
def get_historial_clinico(
    paciente_id: str = Query(..., description="ID del paciente a buscar (ej. P001)")
):
    try:
        resultado = q03_historial_paciente.ejecutar(paciente_id)
        if not resultado:
            raise HTTPException(status_code=404, detail=f"No se encontró historial clínico para el paciente {paciente_id}")
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al ejecutar consulta: {str(e)}")

@app.get(
    "/consultas/propietarios-multiples-pacientes", 
    summary="[Q04] Propietarios con más de un paciente registrado",
    description="Motor: Neo4j (cálculo de grado de salida superior a 1 en relación DUEÑO_DE).",
    tags=["Consultas"]
)
def get_propietarios_multiples_pacientes():
    try:
        return q04_propietarios_multi_paciente.ejecutar()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al ejecutar consulta: {str(e)}")

@app.get(
    "/consultas/veterinarios-consultas-recientes", 
    summary="[Q05] Veterinarios activos y consultas en los últimos 60 días",
    description="Motor: MongoDB (agregación con $match por fecha y $group para conteo).",
    tags=["Consultas"]
)
def get_veterinarios_consultas_recientes():
    try:
        return q05_vets_consultas_60d.ejecutar()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al ejecutar consulta: {str(e)}")

@app.get(
    "/consultas/pacientes-vacunas-vencidas", 
    summary="[Q06] Pacientes con vacunas vencidas",
    description="Motor: MongoDB (comparación de fecha de próxima dosis con la fecha actual).",
    tags=["Consultas"]
)
def get_pacientes_vacunas_vencidas():
    try:
        return q06_vacunas_vencidas.ejecutar()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al ejecutar consulta: {str(e)}")

@app.get(
    "/consultas/top-diagnosticos", 
    summary="[Q07] Top 5 de diagnósticos más frecuentes",
    description="Motor: MongoDB (agrupación y ordenamiento descendente de diagnósticos).",
    tags=["Consultas"]
)
def get_top_diagnosticos():
    try:
        return q07_top5_diagnosticos.ejecutar()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al ejecutar consulta: {str(e)}")

@app.get(
    "/consultas/stock-critico", 
    summary="[Q08] Stock de productos con menos de 50 unidades y su proveedor",
    description="Motor: MongoDB (filtro por unidades y precio unitario).",
    tags=["Consultas"]
)
def get_stock_critico():
    try:
        return q08_stock_bajo.ejecutar()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al ejecutar consulta: {str(e)}")

@app.get(
    "/consultas/consultas-control-baratas", 
    summary="[Q09] Consultas de control con costo menor a $5.000",
    description="Motor: MongoDB (búsqueda por motivo regex y costo menor a 5000).",
    tags=["Consultas"]
)
def get_consultas_control_baratas():
    try:
        return q09_consultas_control.ejecutar()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al ejecutar consulta: {str(e)}")

@app.get(
    "/consultas/pacientes-por-sucursal", 
    summary="[Q10] Pacientes atendidos en una sucursal específica",
    description="Motor: Neo4j (traversal completo Sucursal <- TRABAJA_EN - Vet <- REALIZADA_POR - Consulta <- ATENDIDO_EN - Paciente).",
    tags=["Consultas"]
)
def get_pacientes_por_sucursal(
    sucursal: str = Query(..., description="Nombre de la sucursal (ej. Palermo, Belgrano, Caballito)")
):
    try:
        return q10_pacientes_por_sucursal.ejecutar(sucursal)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al ejecutar consulta: {str(e)}")

@app.get(
    "/consultas/ingresos-mensuales-veterinarios", 
    summary="[Q11] Ingresos totales por veterinario en el mes actual",
    description="Motor: MongoDB (agregación con filtrado por rango de fechas del mes actual, agrupación y lookup de nombres).",
    tags=["Consultas"]
)
def get_ingresos_mensuales_veterinarios():
    try:
        return q11_ingresos_por_vet.ejecutar()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al ejecutar consulta: {str(e)}")
