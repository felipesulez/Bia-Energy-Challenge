import csv
from datetime import datetime
from pathlib import Path

from assignment_engine.domain.absence import Absence
from assignment_engine.domain.record import Record
from assignment_engine.domain.user import User


def load_users(file_path: Path) -> list[User]:
    users: list[User] = []

    with file_path.open(
        mode="r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            capacidad_maxima = (
                int(row["capacidad_maxima"])
                if row["capacidad_maxima"]
                else None
            )

            fecha_ingreso = (
                datetime.strptime(
                    row["fecha_ingreso"],
                    "%Y-%m-%d",
                ).date()
                if row["fecha_ingreso"]
                else None
            )

            equipo_id = (
                int(row["equipo_id"])
                if row["equipo_id"]
                else None
            )

            users.append(
                User(
                    id=int(row["id"]),
                    nombre=row["nombre"],
                    email=row["email"],
                    rol=row["rol"],
                    equipo_id=equipo_id,
                    zona=row["zona"] or None,
                    segmento_experto=(
                        row["segmento_experto"] or None
                    ),
                    capacidad_maxima=capacidad_maxima,
                    fecha_ingreso=fecha_ingreso,
                    activo=row["activo"].strip().lower() == "true",
                )
            )

    return users


def load_absences(file_path: Path) -> list[Absence]:
    absences: list[Absence] = []

    with file_path.open(
        mode="r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            desde = datetime.strptime(
                row["desde"],
                "%Y-%m-%d",
            ).date()

            hasta = (
                datetime.strptime(
                    row["hasta"],
                    "%Y-%m-%d",
                ).date()
                if row["hasta"]
                else None
            )

            absences.append(
                Absence(
                    id=int(row["id"]),
                    usuario_id=int(row["usuario_id"]),
                    desde=desde,
                    hasta=hasta,
                    motivo=row["motivo"] or None,
                )
            )

    return absences


def load_records(file_path: Path) -> list[Record]:
    records: list[Record] = []

    with file_path.open(
        mode="r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            empleados = (
                int(row["empleados"])
                if row["empleados"]
                else None
            )

            ingresos_estimados = (
                float(row["ingresos_estimados"])
                if row["ingresos_estimados"]
                else None
            )

            fecha_creacion = datetime.strptime(
                row["fecha_creacion"],
                "%Y-%m-%d",
            )

            records.append(
                Record(
                    id=int(row["id"]),
                    razon_social=row["razon_social"],
                    nit=row["nit"],
                    sector=row["sector"] or None,
                    empleados=empleados,
                    ingresos_estimados=ingresos_estimados,
                    ciudad=row["ciudad"],
                    zona=row["zona"] or None,
                    fuente=row["fuente"],
                    notas=row["notas"] or None,
                    estado=row["estado"],
                    fecha_creacion=fecha_creacion,
                )
            )

    return records