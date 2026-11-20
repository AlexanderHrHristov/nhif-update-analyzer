
from app.database.db import initialize_database
from app.ui.main_window import MainWindow


def main():
    initialize_database()

    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
