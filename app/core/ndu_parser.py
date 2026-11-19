
from pathlib import Path
from decimal import Decimal, InvalidOperation

from app.database.models import NDUProduct


class NDUParser:
    EXPECTED_FIELDS = 22

    def parse_line(self, line: str) -> NDUProduct:
        """Превръща един NDU ред в NDUProduct."""

        fields = line.strip().split("|")

        if len(fields) != self.EXPECTED_FIELDS:
            raise ValueError(
                f"Очаквани са {self.EXPECTED_FIELDS} полета, "
                f"но са намерени {len(fields)}."
            )

        try:
            return NDUProduct(
                atc_code=fields[0],
                inn=fields[1],
                nhif_code=fields[2],
                name=fields[3],
                manufacturer=fields[4],
                strength=fields[5],
                package_text=fields[6],
                package_quantity=fields[7],
                pharmaceutical_form=fields[8],
                flag_10=fields[9],
                item_type=fields[10],
                field_12=fields[11],
                prescription_group=fields[12],
                flag_14=fields[13],
                reimbursement_value=Decimal(fields[14]),
                price_source=fields[15],
                flag_17=fields[16],
                package_price=Decimal(fields[17]),
                patient_difference=Decimal(fields[18]),
                flag_20=fields[19],
                national_number=fields[20],
                status_flag=fields[21],
            )
        except InvalidOperation as exc:
            raise ValueError(
                f"Невалидна финансова стойност: {line[:100]}"
            ) from exc

    def parse_file(self, file_path: str | Path) -> list[NDUProduct]:
        """Прочита целия NDU файл."""

        file_path = Path(file_path)
        products = []
        seen_codes = set()

        with file_path.open(encoding="cp1251") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                # НЗОК използва EOF като маркер за край.
                if not line or line == "EOF":
                    continue

                try:
                    product = self.parse_line(line)
                except ValueError as exc:
                    raise ValueError(
                        f"Грешка на ред {line_number}: {exc}"
                    ) from exc

                if not product.nhif_code:
                    raise ValueError(
                        f"Липсва НЗОК код на ред {line_number}"
                    )

                if product.nhif_code in seen_codes:
                    raise ValueError(
                        f"Дублиран НЗОК код: {product.nhif_code}"
                    )

                seen_codes.add(product.nhif_code)
                products.append(product)

        return products

