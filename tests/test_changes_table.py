
import customtkinter as ctk

from app.core.change_builder import build_change_rows
from app.database.repository import ProductRepository
from app.ui.changes_table import ChangesTable
from datetime import date


def main():
    repository = ProductRepository()

    old_batch = repository.get_batch_by_date(
        date(2026, 8, 1)
    )

    new_batch = repository.get_batch_by_date(
        date(2026, 8, 16)
    )

    old_products = repository.get_products(
        old_batch["id"]
    )

    new_products = repository.get_products(
        new_batch["id"]
    )

    rows = build_change_rows(
        old_products,
        new_products
    )

    app = ctk.CTk()
    app.title("NHIF Changes Table - Test")
    app.geometry("1200x600")

    table = ChangesTable(app)
    table.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=15
    )

    table.load_rows(rows)

    app.mainloop()


if __name__ == "__main__":
    main()
