import sqlite3

DB_PATH = "expenses.db"


def create_db():
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL CHECK (amount > 0),
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT DEFAULT ''
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL UNIQUE,
                monthly_limit REAL NOT NULL CHECK (monthly_limit > 0)
            )
            """
        )


def add_expense(amount, category, date, description=""):
    if amount <= 0:
        raise ValueError("Amount must be greater than zero")
    if not category.strip():
        raise ValueError("Category cannot be empty")

    with sqlite3.connect(DB_PATH) as db:
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO expenses (amount, category, date, description)
            VALUES (?, ?, ?, ?)
            """,
            (amount, category.strip(), date, description.strip()),
        )
        return cursor.lastrowid


def get_expenses(limit=None):
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.cursor()
        if limit is not None:
            cursor.execute(
                """
                SELECT id, amount, category, date, description
                FROM expenses
                ORDER BY date DESC
                LIMIT ?
                """,
                (limit,),
            )
        else:
            cursor.execute(
                """
                SELECT id, amount, category, date, description
                FROM expenses
                ORDER BY date DESC
                """
            )
        return cursor.fetchall()


def delete_expense(expense_id):
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        return cursor.rowcount > 0


def update_expense(expense_id, amount, category, date, description=""):
    if amount <= 0:
        raise ValueError("Amount must be greater than zero")
    if not category.strip():
        raise ValueError("Category cannot be empty")

    with sqlite3.connect(DB_PATH) as db:
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE expenses
            SET amount = ?, category = ?, date = ?, description = ?
            WHERE id = ?
            """,
            (amount, category.strip(), date, description.strip(), expense_id),
        )
        return cursor.rowcount > 0


def get_total_expenses(start_date, end_date):
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT COALESCE(SUM(amount), 0.0)
            FROM expenses
            WHERE date BETWEEN ? AND ?
            """,
            (start_date, end_date),
        )
        return cursor.fetchone()[0]


def set_budget(category, amount):
    if amount <= 0:
        raise ValueError("Budget limit must be greater than zero")
    if not category.strip():
        raise ValueError("Category cannot be empty")

    with sqlite3.connect(DB_PATH) as db:
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO budgets (category, monthly_limit)
            VALUES (?, ?)
            ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit
            """,
            (category.strip(), amount),
        )
        return cursor.lastrowid


def get_budget(category):
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT monthly_limit
            FROM budgets
            WHERE category = ?
            """,
            (category,),
        )
        row = cursor.fetchone()
        return row[0] if row else None


def get_all_budgets():
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.cursor()
        cursor.execute("SELECT category, monthly_limit FROM budgets ORDER BY category ASC")
        return cursor.fetchall()


def get_expenses_by_category(category):
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, amount, date, description
            FROM expenses
            WHERE category = ?
            ORDER BY date DESC
            """,
            (category,),
        )
        return cursor.fetchall()

def delete_budget(category):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM budgets WHERE category = ?",
        (category,)
    )

    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return deleted
def get_expenses_by_date(date):
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, amount, category, date, description
            FROM expenses
            WHERE date = ?
            ORDER BY date DESC
            """,
            (date,),
        )
        return cursor.fetchall()


if __name__ == "__main__":
    create_db()
    print("Database created successfully")
