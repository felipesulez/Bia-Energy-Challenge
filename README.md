# Motor de Asignación Comercial

Motor de asignación de registros comerciales desarrollado como una API REST y una interfaz web para automatizar la distribución de registros entre usuarios, manteniendo trazabilidad, historial y explicabilidad de las decisiones.

## Tecnologías

### Backend

* Python 3.12
* FastAPI
* Pydantic
* Uvicorn
* SQLite
* Pytest

### Frontend

* React
* Vite
* JavaScript
* CSS

### Herramientas

* Git
* GitHub
* REST API
* Swagger / OpenAPI

## Arquitectura

La solución separa la interfaz, la API, la lógica de negocio y la persistencia:

```text
React + Vite
     |
     | HTTP / REST
     v
FastAPI
     |
     v
Assignment Service
     |
     v
Assignment Engine
     |
     v
SQLite
```

El motor de asignación concentra las reglas de negocio y permite mantener la lógica independiente de la interfaz y de la capa HTTP.

## Funcionalidades

### Preview

Permite generar una propuesta de asignación sin modificar los datos persistidos.

La respuesta incluye información utilizada para explicar la decisión:

* Usuario seleccionado.
* Método de asignación.
* Score de zona.
* Score de carga.
* Score total.
* Capacidad y utilización.
* Estado geográfico.
* Explicación de la decisión.

### Ejecución

Permite ejecutar las asignaciones propuestas y persistir los resultados.

La operación es transaccional: las asignaciones y el cambio de estado de los registros se guardan juntos o no se guarda nada. Además es idempotente, de modo que ejecutar dos veces no duplica asignaciones.

### Historial

Las asignaciones se conservan como registros históricos.

El sistema permite consultar:

* Asignaciones activas.
* Asignaciones históricas.
* Usuario asignado.
* Método utilizado.
* Scores.
* Carga antes y después.
* Información geográfica.
* Usuario que ejecutó la operación.

### Explicabilidad

Cada asignación conserva la información necesaria para responder:

> ¿Por qué este registro fue asignado a este usuario?

La explicación considera los criterios utilizados por el motor, incluyendo coincidencia geográfica, carga y puntuación total.

### Reasignación

Una asignación activa puede ser reasignada sin eliminar el registro anterior.

Las nuevas asignaciones mantienen una relación con la asignación que reemplazan, permitiendo reconstruir la evolución de una decisión.

Ejemplo:

```text
Asignación #1
Registro 1 → Usuario 15
      |
      v
Asignación #72
Registro 1 → Usuario 16
      |
      v
Asignación #73
Registro 1 → Usuario 15
```

En este caso, la asignación #73 queda activa y las anteriores permanecen como históricas.

## Método de asignación

El método implementado actualmente es `weighted_rules`, que es determinista: las mismas entradas producen siempre el mismo resultado.

1. **Elegibilidad:** se excluyen los usuarios con ausencia activa o sin capacidad disponible.
2. **Score total:** cada candidato recibe un puntaje que combina la coincidencia de zona y la carga. Gana el mayor.
3. **Desempate por capacidad:** si hay empate en el score, gana quien tenga más capacidad disponible.
4. **Desempate por ID:** si el empate persiste, gana el menor ID de usuario.

Cuando ningún candidato elegible está en la zona del registro, se aplica un fallback geográfico y la decisión queda registrada como tal en la traza.

El diseño permite incorporar posteriormente nuevos métodos de asignación sin depender de la interfaz web.

## API

### Health check

```http
GET /health
```

### Consultar historial

```http
GET /assignments
```

### Consultar detalle

```http
GET /assignments/{assignment_id}
```

### Generar preview

```http
POST /assignments/preview
```

```json
{
  "evaluation_date": "2026-10-04"
}
```

### Ejecutar asignaciones

```http
POST /assignments/execute
```

```json
{
  "evaluation_date": "2026-10-04",
  "executed_by": "felipe"
}
```

### Reasignar

```http
POST /assignments/{assignment_id}/reassign
```

```json
{
  "evaluation_date": "2026-10-04",
  "executed_by": "felipe"
}
```

La documentación interactiva de la API está disponible mediante Swagger UI en:

```text
http://127.0.0.1:8000/docs
```

## Ejecución local

### Backend

Desde la raíz del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Iniciar la API:

```bash
PYTHONPATH=backend:ai-engine/src uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

La base de datos SQLite se crea automáticamente en `data/assignment.db` la primera vez que se usa la API. Para empezar desde cero, basta con borrar ese archivo.

El backend debe permitir CORS para `http://localhost:5173`, que es el origen del frontend en desarrollo.

### Frontend

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## Pruebas

Las pruebas automatizadas se ejecutan desde la raíz del proyecto:

```bash
PYTHONPATH=backend:ai-engine/src pytest
```

Las pruebas cubren los principales flujos del sistema, incluyendo:

* Motor de asignación.
* Preview.
* Ejecución.
* Idempotencia.
* Persistencia.
* Historial.
* Detalle de asignaciones.
* Reasignación.
* Estado activo.
* Trazabilidad.

## Estado del proyecto

MVP funcional con flujo completo de:

```text
Registros pendientes
        |
        v
     Preview
        |
        v
    Ejecución
        |
        v
   Asignación
        |
        +----> Historial
        |
        +----> Explicabilidad
        |
        +----> Reasignación
```

## Limitaciones conocidas

* Los usuarios se cargan desde archivos CSV en cada petición, sin incorporar las cargas de asignaciones ya persistidas. Con los datos actuales funciona, pero la capacidad calculada en reasignaciones puede no reflejar la realidad.
* No hay autenticación: el campo `executed_by` lo envía el cliente.
* Los scores se comparan como números de punto flotante, sin redondeo previo.

## Autor

**Felipe Sulez**