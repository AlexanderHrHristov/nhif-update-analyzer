
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk


class ChangesTable(ctk.CTkFrame):

    COLUMNS = [
        ("national_number", "National №", 130),
        ("nhif_code", "НЗОК код", 120),
        ("product_name", "Продукт", 750),
        ("manufacturer", "Производител", 500),
        ("change_type", "Вид промяна", 190),
        ("reimbursement_percent", "Реимб. %", 130),
        ("old_reimbursement", "Стара реимб.", 150),
        ("new_reimbursement", "Нова реимб.", 150),
        ("old_price", "Стара цена", 150),
        ("new_price", "Нова цена", 150),
        ("changed_fields", "Променени полета", 500),
]

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.configure(fg_color="#242424")

        self._configure_style()
        self._build_table()

    
    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Основна таблица
        style.configure(
            "NHIF.Treeview",
            background="#242424",
            foreground="white",
            fieldbackground="#242424",
            font=("Segoe UI", 16),
            rowheight=46,
            borderwidth=0,
        )

        # Заглавия на колоните
        style.configure(
            "NHIF.Treeview.Heading",
            background="#343638",
            foreground="white",
            font=("Segoe UI", 14, "bold"),
            padding=(12, 14),
        )

        # Избран ред
        style.map(
            "NHIF.Treeview",
            background=[("selected", "#1F6AA5")],
            foreground=[("selected", "white")],
        )


    def _build_table(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        column_ids = [
            column[0] for column in self.COLUMNS
        ]

        self.tree = ttk.Treeview(
            self,
            columns=column_ids,
            show="headings",
            style="NHIF.Treeview",
        )

        for column_id, title, width in self.COLUMNS:
            self.tree.heading(
                column_id,
                text=title
            )

            self.tree.column(
                column_id,
                width=width,
                minwidth=80,
                stretch=False
            )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.vertical_scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview
        )
        self.vertical_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.horizontal_scrollbar = ttk.Scrollbar(
            self,
            orient="horizontal",
            command=self.tree.xview
        )
        self.horizontal_scrollbar.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        self.tree.configure(
            yscrollcommand=self.vertical_scrollbar.set,
            xscrollcommand=self.horizontal_scrollbar.set,
        )

    def load_rows(self, rows):
        """Зарежда списък от ProductChangeRow."""

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            values = [
                row.national_number,
                row.nhif_code,
                row.product_name,
                row.manufacturer,
                row.change_type,
                self._format_value(
                    row.reimbursement_percent
                ),
                self._format_value(
                    row.old_reimbursement
                ),
                self._format_value(
                    row.new_reimbursement
                ),
                self._format_value(row.old_price),
                self._format_value(row.new_price),
                row.changed_fields,
            ]

            self.tree.insert(
                "",
                "end",
                values=values
            )

    @staticmethod
    def _format_value(value):
        if value is None:
            return ""

        return str(value)
