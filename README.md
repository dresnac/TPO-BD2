# TPO VetSalud — Base de Datos II

Trabajo Práctico Obligatorio — Base de Datos II — ITBA — 2026 1C.

Sistema de gestión para la clínica veterinaria VetSalud S.A. con persistencia políglota sobre dos motores NoSQL de paradigmas distintos.

## Motores

- **MongoDB 7** — modelo documental para las entidades del dominio (pacientes, propietarios, veterinarios, consultas, vacunaciones, cirugías, stock farmacéutico).
- **Neo4j 5** — modelo de grafo para representar las relaciones entre entidades (propietario→paciente, paciente→consulta, vet→sucursal, etc.) y resolver las consultas que se expresan naturalmente como traversals.

## Consultas y servicios

| # | Descripción | Motor |
|---|---|---|
| Q1 | Pacientes activos de un propietario | Neo4j |
| Q2 | Consultas en estado seguimiento | MongoDB |
| Q3 | Historial clínico unificado de un paciente | MongoDB |
| Q4 | Propietarios con más de un paciente | Neo4j |
| Q5 | Veterinarios con consultas en los últimos 60 días | MongoDB |
| Q6 | Pacientes con vacunas vencidas | MongoDB |
| Q7 | Top 5 diagnósticos más frecuentes | MongoDB |
| Q8 | Productos con menos de 50 unidades en stock | MongoDB |
| Q9 | Consultas de control con costo menor a $5.000 | MongoDB |
| Q10 | Pacientes atendidos por sucursal | Neo4j |
| Q11 | Ingresos por veterinario en el mes actual | MongoDB |
| Q12 | Propietarios sin consultas en el último año | Neo4j |
| Q13 | ABM de propietarios | Mongo + Neo4j |
| Q14 | Alta de consulta | Mongo + Neo4j |
| Q15 | Descuento de stock farmacéutico | MongoDB |

Cada consulta vive en su propio módulo `src/consultas/qNN_*.py` y expone una función `ejecutar(args=None)` que devuelve el resultado como `list[dict]` o `dict`.

## Datos

- Datasets originales de la cátedra en `datasets_vetsalud/`.
- Diez registros adicionales por colección en `data/extras/`.
- Dataset propio de cirugías (entidad mencionada en el enunciado sin CSV provisto) en `data/cirugias.csv` y `data/extras/cirugias_extras.csv`.
