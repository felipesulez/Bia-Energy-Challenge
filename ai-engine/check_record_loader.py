from pathlib import Path

from assignment_engine.data.loader import load_records


DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "raw"
    / "data-opcion-a"
    / "data-opcion-a"
)

records = load_records(
    DATA_DIR / "registros.csv"
)

print("=== PRUEBA RECORD LOADER ===")
print("Total de registros:", len(records))

print("\n=== PRIMER REGISTRO ===")

record = records[0]

print("ID:", record.id)
print("Razón social:", record.razon_social)
print("NIT:", record.nit)
print("Sector:", record.sector)
print("Empleados:", record.empleados)
print("Ingresos:", record.ingresos_estimados)
print("Ciudad:", record.ciudad)
print("Zona:", record.zona)
print("Zona normalizada:", record.zona_normalizada)
print("Fuente:", record.fuente)
print("Notas:", record.notas)
print("Estado:", record.estado)
print("Fecha creación:", record.fecha_creacion)

print("\n=== CAMPOS FALTANTES ===")

print(
    "Sector:",
    sum(record.sector is None for record in records),
)

print(
    "Empleados:",
    sum(record.empleados is None for record in records),
)

print(
    "Ingresos:",
    sum(record.ingresos_estimados is None for record in records),
)

print(
    "Zona:",
    sum(record.zona is None for record in records),
)

print(
    "Notas:",
    sum(record.notas is None for record in records),
)