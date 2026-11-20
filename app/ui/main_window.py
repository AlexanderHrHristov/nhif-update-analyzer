import zipfile
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from app.core.change_builder import build_change_rows
from app.core.change_row import build_change_row
from app.core.diff_engine import DiffEngine
from app.core.zip_importer import ZIPImporter
from app.database.repository import ProductRepository
from app.ui.changes_table import ChangesTable

from app.core.excel_exporter import ExcelExporter

class MainWindow(ctk.CTk):
    METRICS = [
        ("new", "Нови продукти"),
        ("removed", "Отпаднали"),
        ("financial", "Финансови промени"),
        ("other", "Други промени"),
        ("pending", "Преходен флаг"),
        ("total", "Общо продукти"),
    ]

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("NHIF Update Analyzer")
        self.geometry("1350x850")
        self.minsize(1000, 650)

        self.repository = ProductRepository()
        self.engine = DiffEngine()
        self.current_change_rows = []
        self.current_new_products = []
        self.current_old_products = []
        self.current_result = None
        self.active_filter = "financial"
        self.build_ui()
        self.load_dashboard()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(18, 8))
        ctk.CTkLabel(
            header, text="НЗОК — Анализатор на актуализации",
            font=ctk.CTkFont(size=25, weight="bold"),
        ).pack(side="left")
        ctk.CTkButton(
            header, text="Импортирай ZIP", width=160, height=40,
            command=self.select_zip,
        ).pack(side="right")

        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.tabs.add("Анализ")
        self.tabs.add("История")
        self.tabs.set("Анализ")

        analysis = self.tabs.tab("Анализ")
        analysis.grid_columnconfigure(0, weight=1)
        analysis.grid_rowconfigure(4, weight=1)

        self.comparison_label = ctk.CTkLabel(
            analysis, text="Зареждане...",
            font=ctk.CTkFont(size=17, weight="bold"),
        )
        self.comparison_label.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 10))

        compare_frame = ctk.CTkFrame(analysis)
        compare_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 12))
        for column in (0, 1):
            compare_frame.grid_columnconfigure(column, weight=1)
        ctk.CTkLabel(compare_frame, text="Предходна актуализация").grid(
            row=0, column=0, pady=(12, 3)
        )
        ctk.CTkLabel(compare_frame, text="Нова актуализация").grid(
            row=0, column=1, pady=(12, 3)
        )
        self.old_date_menu = ctk.CTkOptionMenu(
            compare_frame, values=["Зареждане..."], width=220,
        )
        self.old_date_menu.grid(row=1, column=0, padx=12, pady=(0, 12))
        self.new_date_menu = ctk.CTkOptionMenu(
            compare_frame, values=["Зареждане..."], width=220,
        )
        self.new_date_menu.grid(row=1, column=1, padx=12, pady=(0, 12))
        ctk.CTkButton(
            compare_frame, text="Сравни актуализациите", height=38,
            command=self.compare_selected_dates,
        ).grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))

        self.kpi_frame = ctk.CTkFrame(analysis, fg_color="transparent")
        self.kpi_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 10))
        for col in range(3):
            self.kpi_frame.grid_columnconfigure(col, weight=1)

        self.kpi_buttons = {}
        self.kpi_labels = {}
        for index, (key, title) in enumerate(self.METRICS):
            button = ctk.CTkButton(
                self.kpi_frame,
                text=f"{title}\n—",
                font=ctk.CTkFont(size=17, weight="bold"),
                height=90, corner_radius=9,
                fg_color="#303030", hover_color="#414141",
                command=lambda selected=key: self.show_category(selected),
            )
            button.grid(
                row=index // 3, column=index % 3,
                padx=5, pady=5, sticky="nsew",
            )
            self.kpi_buttons[key] = button

        
        # Заглавие на таблицата и бутон за Excel
        table_header = ctk.CTkFrame(
            analysis,
            fg_color="transparent",
        )
        table_header.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=10,
            pady=(4, 8),
        )

        self.table_title = ctk.CTkLabel(
            table_header,
            text="Продукти",
            font=ctk.CTkFont(
                size=19,
                weight="bold",
            ),
        )
        self.table_title.pack(side="left")

        self.export_button = ctk.CTkButton(
            table_header,
            text="Експорт в Excel",
            width=170,
            height=38,
            fg_color="#217346",
            hover_color="#185C37",
            command=self.export_to_excel,
        )
        self.export_button.pack(side="right")
     
        
        
        self.changes_table = ChangesTable(analysis)
        self.changes_table.grid(
            row=4, column=0, sticky="nsew", padx=10, pady=(0, 10),
        )

        history_tab = self.tabs.tab("История")
        self.history_frame = ctk.CTkScrollableFrame(history_tab)
        self.history_frame.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(
            self.history_frame, text="История на актуализациите",
            font=ctk.CTkFont(size=21, weight="bold"),
        ).pack(anchor="w", pady=(5, 12))
        self.history_rows_frame = ctk.CTkFrame(self.history_frame)
        self.history_rows_frame.pack(fill="x")

        self.status_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.status_label.pack(anchor="w", padx=30, pady=(0, 8))

    def load_dashboard(self):
        history = self.repository.get_update_history()
        dates = [
            date.fromisoformat(batch["effective_date"]).strftime("%d.%m.%Y")
            for batch in history
        ]
        for widget in self.history_rows_frame.winfo_children():
            widget.destroy()

        for batch in history:
            row = ctk.CTkFrame(self.history_rows_frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=8)
            display_date = date.fromisoformat(
                batch["effective_date"]
            ).strftime("%d.%m.%Y")
            ctk.CTkLabel(row, text=display_date, anchor="w").pack(side="left")
            ctk.CTkLabel(
                row, text=f'{batch["product_count"]} продукта', anchor="e",
            ).pack(side="right")

        if not history:
            self.comparison_label.configure(text="Няма импортирани актуализации")
            self._clear_comparison()
            return

        self.old_date_menu.configure(values=dates)
        self.new_date_menu.configure(values=dates)
        self.new_date_menu.set(dates[0])
        self.old_date_menu.set(dates[1] if len(dates) > 1 else dates[0])

        if len(history) < 2:
            self.comparison_label.configure(
                text="Няма предходна актуализация за сравнение"
            )
            self._clear_comparison()
            return

        self._load_comparison(history[1], history[0], dates[1], dates[0])

    def _clear_comparison(self):
        self.current_change_rows = []
        self.current_new_products = []
        self.current_old_products = []
        self.current_result = None
        self.changes_table.load_rows([])
        self.table_title.configure(text="Продукти (0)")
        for key, title in self.METRICS:
            self.kpi_buttons[key].configure(text=f"{title}\n—")

    def _load_comparison(self, old_batch, new_batch, old_text, new_text):
        old_products = self.repository.get_products(old_batch["id"])
        new_products = self.repository.get_products(new_batch["id"])
        self.current_result = self.engine.compare(old_products, new_products)
        self.current_change_rows = build_change_rows(old_products, new_products)
        self.current_new_products = new_products
        self.current_old_products = old_products

        result = self.current_result
        values = {
            "new": len(result.new_products),
            "removed": len(result.removed_products),
            "financial": len(result.financial_changes),
            "other": len(result.other_changes),
            "pending": len(result.pending_removal),
            "total": len(new_products),
        }
        for key, title in self.METRICS:
            self.kpi_buttons[key].configure(text=f"{title}\n{values[key]}")

        self.comparison_label.configure(text=f"Сравнение: {old_text} → {new_text}")
        self.show_category(self.active_filter)

    def show_category(self, category):
        """Филтрира таблицата според избраната KPI карта."""
        self.active_filter = category
        for key, button in self.kpi_buttons.items():
            button.configure(
                fg_color="#1F6AA5" if key == category else "#303030",
                hover_color="#267AB8" if key == category else "#414141",
            )

        if self.current_result is None:
            return

        if category == "total":
            old_by_code = {p.nhif_code: p for p in self.current_old_products}
            rows = [
                build_change_row(
                    old=old_by_code.get(product.nhif_code),
                    new=product, change_type="Без промяна",
                )
                for product in self.current_new_products
            ]
            changed_by_code = {
                row.nhif_code: row for row in self.current_change_rows
                if row.change_type != "Отпаднал"
            }
            rows = [changed_by_code.get(row.nhif_code, row) for row in rows]
        elif category == "pending":
            # Статус 1 обозначава преходен флаг в NDUProduct.
            codes = {
                product.nhif_code for product in self.current_new_products
                if product.is_pending_removal
            }
            changed_by_code = {
                row.nhif_code: row for row in self.current_change_rows
            }
            rows = [
                changed_by_code.get(
                    product.nhif_code,
                    build_change_row(
                        old=product, new=product,
                        change_type="Преходен флаг",
                        changed_fields="Статус",
                    ),
                )
                for product in self.current_new_products
                if product.nhif_code in codes
            ]
        else:
            rows = [
                row for row in self.current_change_rows
                if (
                    (category == "new" and row.change_type == "Нов")
                    or (category == "removed" and row.change_type == "Отпаднал")
                    or (category == "financial" and "Финансова" in row.change_type)
                    or (category == "other" and "Друга" in row.change_type)
                )
            ]

        title = dict(self.METRICS)[category]
        self.table_title.configure(text=f"{title} — {len(rows)} артикула")
        self.changes_table.load_rows(rows)
        self.visible_change_rows = rows

    def compare_selected_dates(self):
        old_date_text = self.old_date_menu.get()
        new_date_text = self.new_date_menu.get()
        try:
            old_date = date.fromisoformat(
                "-".join(reversed(old_date_text.split(".")))
            )
            new_date = date.fromisoformat(
                "-".join(reversed(new_date_text.split(".")))
            )
        except ValueError:
            messagebox.showerror("Невалидни дати", "Избери валидни актуализации.")
            return

        if old_date >= new_date:
            messagebox.showwarning(
                "Невалидни дати",
                "Предходната актуализация трябва да бъде по-стара от новата.",
            )
            return

        old_batch = self.repository.get_batch_by_date(old_date)
        new_batch = self.repository.get_batch_by_date(new_date)
        if not old_batch or not new_batch:
            messagebox.showerror(
                "Липсваща актуализация", "Една от актуализациите липсва."
            )
            return
        self._load_comparison(old_batch, new_batch, old_date_text, new_date_text)

    def select_zip(self):
        file_path = filedialog.askopenfilename(
            title="Избери актуализация на НЗОК",
            filetypes=[("ZIP archives", "*.zip")],
        )
        if not file_path:
            return
        try:
            importer = ZIPImporter()
            effective_date = importer.detect_effective_date(file_path)
            batch_id, count = importer.import_zip(
                zip_path=file_path, effective_date=effective_date,
            )
            self.load_dashboard()
            self.status_label.configure(
                text=(
                    f"Импортиран: {Path(file_path).name} | "
                    f"Дата: {effective_date:%d.%m.%Y} | Продукти: {count}"
                )
            )
            messagebox.showinfo(
                "Успешен импорт",
                f"Импортирани {count} продукта.\n"
                f"Дата: {effective_date:%d.%m.%Y}\nBatch ID: {batch_id}",
            )
        except ValueError as exc:
            message = str(exc)
            if "вече е импортиран" in message:
                messagebox.showinfo("Вече съществува", message)
            else:
                messagebox.showerror("Грешка при импортиране", message)
        except (FileNotFoundError, zipfile.BadZipFile) as exc:
            messagebox.showerror("Невалиден архив", str(exc))

    
    
    def export_to_excel(self):
        """Експортира показаната категория в Excel."""

        rows = getattr(self, "visible_change_rows", [])

        if not rows:
            messagebox.showwarning(
                "Няма данни",
                "Няма артикули за експортиране.",
            )
            return

        old_date = self.old_date_menu.get().replace(".", "-")
        new_date = self.new_date_menu.get().replace(".", "-")

        category = self.active_filter

        filename = (
            f"NHIF_{old_date}_to_{new_date}_{category}.xlsx"
        )

        file_path = filedialog.asksaveasfilename(
            title="Запази Excel файла",
            defaultextension=".xlsx",
            initialfile=filename,
            filetypes=[
                ("Excel Workbook", "*.xlsx"),
            ],
        )

        if not file_path:
            return

        try:
            exporter = ExcelExporter()
            exporter.export(rows, file_path)

            self.status_label.configure(
                text=f"Експортирани {len(rows)} артикула."
            )

            messagebox.showinfo(
                "Успешен експорт",
                f"Експортирани {len(rows)} артикула.\n\n"
                f"Файл: {file_path}",
            )

        except (OSError, PermissionError) as exc:
            messagebox.showerror(
                "Грешка при експортиране",
                str(exc),
            )
