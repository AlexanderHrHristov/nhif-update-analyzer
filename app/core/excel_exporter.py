
from decimal import Decimal
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import (
    Alignment,
    Font,
    PatternFill,
)
from openpyxl.utils import get_column_letter


class ExcelExporter:
    HEADERS = [
        "National number",
        "НЗОК код",
        "Име на продукта",
        "Производител",
        "Вид промяна",
        "% реимбурсация",
        "Стара реимбурсна стойност",
        "Нова реимбурсна стойност",
        "Стара цена на опаковка",
        "Нова цена на опаковка",
        "Променени полета",
    ]

    WIDTHS = [18, 14, 55, 40, 23, 20, 27, 27, 25, 25, 55]

    @staticmethod
    def _safe_text(value):
        """Предпазва текстовите клетки от Excel формули."""
        text = "" if value is None else str(value)

        if text.lstrip().startswith(("=", "+", "-", "@")):
            return "'" + text

        return text

    @staticmethod
    def _number(value):
        if value is None:
            return None
        return float(value)

    def export(self, rows, file_path):
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Продукти"

        sheet.append(self.HEADERS)

        for row in rows:
            sheet.append([
                self._safe_text(row.national_number),
                self._safe_text(row.nhif_code),
                self._safe_text(row.product_name),
                self._safe_text(row.manufacturer),
                self._safe_text(row.change_type),
                (
                    self._number(row.reimbursement_percent)
                    / 100
                    if row.reimbursement_percent is not None
                    else None
                ),
                self._number(row.old_reimbursement),
                self._number(row.new_reimbursement),
                self._number(row.old_price),
                self._number(row.new_price),
                self._safe_text(row.changed_fields),
            ])

        # Заглавен ред
        for cell in sheet[1]:
            cell.fill = PatternFill(
                "solid",
                fgColor="17365D",
            )
            cell.font = Font(
                name="Calibri",
                size=12,
                bold=True,
                color="FFFFFF",
            )
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True,
            )

        sheet.row_dimensions[1].height = 42

        # Ширини на колоните
        for index, width in enumerate(self.WIDTHS, start=1):
            letter = get_column_letter(index)
            sheet.column_dimensions[letter].width = width

        # Форматиране на данните
        for row_index in range(2, sheet.max_row + 1):
            for col_index in range(1, 12):
                cell = sheet.cell(row_index, col_index)
                cell.font = Font(name="Calibri", size=11)
                cell.alignment = Alignment(vertical="center")

                if row_index % 2 == 0:
                    cell.fill = PatternFill(
                        "solid",
                        fgColor="EDF3F8",
                    )

            # Процент на реимбурсация
            sheet.cell(row_index, 6).number_format = "0.00%"

            # Финансови стойности
            for col_index in range(7, 11):
                sheet.cell(
                    row_index, col_index
                ).number_format = '#,##0.00'

            sheet.row_dimensions[row_index].height = 22

        # Автоматични филтри
        sheet.auto_filter.ref = sheet.dimensions

        # Фиксираме заглавния ред и първите два идентификатора
        sheet.freeze_panes = "C2"

        file_path = Path(file_path)
        workbook.save(file_path)

        return file_path
