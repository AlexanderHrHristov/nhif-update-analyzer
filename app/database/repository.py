
import sqlite3
from datetime import date
from pathlib import Path

from app.database.db import get_connection
from app.database.models import NDUProduct


class ProductRepository:

    def import_snapshot(
        self,
        effective_date: date,
        file_path: Path,
        checksum: str,
        products: list[NDUProduct],
    ) -> int:

        with get_connection() as connection:
            # Проверяваме дали вече сме импортнали файла.
            existing = connection.execute(
                """
                SELECT id
                FROM update_batches
                WHERE checksum = ?
                """,
                (checksum,),
            ).fetchone()

            if existing:
                raise ValueError(
                    "Този NDU файл вече е импортиран."
                )

            # Записваме новата актуализация.
            cursor = connection.execute(
                """
                INSERT INTO update_batches (
                    effective_date,
                    filename,
                    checksum
                )
                VALUES (?, ?, ?)
                """,
                (
                    effective_date.isoformat(),
                    file_path.name,
                    checksum,
                ),
            )

            batch_id = cursor.lastrowid

            # Подготвяме всички продукти.
            rows = [
                (
                    batch_id,
                    p.nhif_code,
                    p.atc_code,
                    p.inn,
                    p.name,
                    p.manufacturer,
                    p.strength,
                    p.package_text,
                    p.package_quantity,
                    p.pharmaceutical_form,
                    p.flag_10,
                    p.item_type,
                    p.field_12,
                    p.prescription_group,
                    p.flag_14,
                    str(p.reimbursement_value),
                    p.price_source,
                    p.flag_17,
                    str(p.package_price),
                    str(p.patient_difference),
                    p.flag_20,
                    p.national_number,
                    p.status_flag,
                )
                for p in products
            ]

            connection.executemany(
                """
                INSERT INTO product_snapshots (
                    batch_id,
                    nhif_code,
                    atc_code,
                    inn,
                    name,
                    manufacturer,
                    strength,
                    package_text,
                    package_quantity,
                    pharmaceutical_form,
                    flag_10,
                    item_type,
                    field_12,
                    prescription_group,
                    flag_14,
                    reimbursement_value,
                    price_source,
                    flag_17,
                    package_price,
                    patient_difference,
                    flag_20,
                    national_number,
                    status_flag
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?
                )
                """,
                rows,
            )

        return batch_id

    def count_products(self, batch_id: int) -> int:
        with get_connection() as connection:
            result = connection.execute(
                """
                SELECT COUNT(*)
                FROM product_snapshots
                WHERE batch_id = ?
                """,
                (batch_id,),
            ).fetchone()

            return result[0]



    def get_products(self, batch_id: int) -> list[NDUProduct]:
        """Зарежда продуктите от конкретна актуализация."""

        from decimal import Decimal

        with get_connection() as connection:
            connection.row_factory = sqlite3.Row

            rows = connection.execute(
                """
                SELECT *
                FROM product_snapshots
                WHERE batch_id = ?
                ORDER BY nhif_code
                """,
                (batch_id,),
            ).fetchall()

        products = []

        for row in rows:
            product = NDUProduct(
                atc_code=row["atc_code"],
                inn=row["inn"],
                nhif_code=row["nhif_code"],
                name=row["name"],
                manufacturer=row["manufacturer"],
                strength=row["strength"],
                package_text=row["package_text"],
                package_quantity=row["package_quantity"],
                pharmaceutical_form=row["pharmaceutical_form"],
                flag_10=row["flag_10"],
                item_type=row["item_type"],
                field_12=row["field_12"],
                prescription_group=row["prescription_group"],
                flag_14=row["flag_14"],
                reimbursement_value=Decimal(
                    row["reimbursement_value"]
                ),
                price_source=row["price_source"],
                flag_17=row["flag_17"],
                package_price=Decimal(
                    row["package_price"]
                ),
                patient_difference=Decimal(
                    row["patient_difference"]
                ),
                flag_20=row["flag_20"],
                national_number=row["national_number"],
                status_flag=row["status_flag"],
            )

            products.append(product)

        return products



    def get_previous_batch(self, effective_date: date):
        """Намира последната актуализация преди зададената дата."""

        with get_connection() as connection:
            connection.row_factory = sqlite3.Row

            row = connection.execute(
                """
                SELECT id, effective_date, filename
                FROM update_batches
                WHERE effective_date < ?
                ORDER BY effective_date DESC, id DESC
                LIMIT 1
                """,
                (effective_date.isoformat(),),
            ).fetchone()

        return dict(row) if row else None



    def get_batch_by_date(self, effective_date: date):
        """Намира импортната актуализация за конкретна дата."""

        with get_connection() as connection:
            connection.row_factory = sqlite3.Row

            row = connection.execute(
                """
                SELECT id, effective_date, filename
                FROM update_batches
                WHERE effective_date = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (effective_date.isoformat(),),
            ).fetchone()

        return dict(row) if row else None
