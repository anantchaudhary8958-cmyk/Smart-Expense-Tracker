
import database
import datetime
import calendar


def _validate_date(date_str):
    """Date ka format YYYY-MM-DD check karta hai."""
    if not isinstance(date_str, str):
        raise ValueError("Date must be in YYYY-MM-DD format")

    try:
        parsed_date = datetime.datetime.strptime(
            date_str, "%Y-%m-%d"
        )
    except ValueError:
        raise ValueError(
            "Invalid date format. Please use YYYY-MM-DD"
        ) from None

    if parsed_date.strftime("%Y-%m-%d") != date_str:
        raise ValueError(
            "Invalid date format. Please use YYYY-MM-DD"
        )

    return date_str


def validate_expense_date(amount, category, date_str):
    """Amount, category aur date validate karta hai."""
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        raise ValueError("Enter a valid amount") from None

    if amount <= 0:
        raise ValueError("Amount must be greater than zero")

    if not isinstance(category, str) or not category.strip():
        raise ValueError("Category cannot be empty")

    _validate_date(date_str)

    return amount, category.strip()


def _clean_description(description):
    """Description ko safely clean karta hai."""
    if description is None:
        return ""

    if not isinstance(description, str):
        raise ValueError("Description must be text")

    return description.strip()


def add_new_expense(
    amount, category, date_str, description=""
):
    """Validated expense database mein add karta hai."""
    valid_amount, valid_category = validate_expense_date(
        amount, category, date_str
    )

    return database.add_expense(
        amount=valid_amount,
        category=valid_category,
        date=date_str,
        description=_clean_description(description),
    )


def fetch_all_expenses(limit=None):
    """Expenses ko dictionaries ki list mein return karta hai."""
    rows = database.get_expenses(limit=limit)

    expenses = []

    for row in rows:
        expenses.append({
            "id": row[0],
            "amount": row[1],
            "category": row[2],
            "date": row[3],
            "description": row[4],
        })

    return expenses


def remove_expenses(expense_id):
    """ID se expense delete karta hai."""
    return database.delete_expense(expense_id)


def edit_expenses(
    expense_id, amount, category, date_str, description=""
):
    """Existing expense ko edit karta hai."""
    valid_amount, valid_category = validate_expense_date(
        amount, category, date_str
    )

    return database.update_expense(
        expense_id=expense_id,
        amount=valid_amount,
        category=valid_category,
        date=date_str,
        description=_clean_description(description),
    )


def get_total_spending(start_date=None, end_date=None):
    """Date range ya overall spending calculate karta hai."""
    if start_date is not None:
        _validate_date(start_date)

    if end_date is not None:
        _validate_date(end_date)

    if start_date and end_date and start_date > end_date:
        raise ValueError(
            "Start date cannot be after end date"
        )

    start = start_date or "0001-01-01"
    end = end_date or "9999-12-31"

    return database.get_total_expenses(start, end)


def get_monthly_spending(year, month):
    """Kisi particular year aur month ka total nikalta hai."""
    try:
        year = int(year)
        month = int(month)
    except (ValueError, TypeError):
        raise ValueError("Enter a valid year and month") from None

    if year < 1 or not 1 <= month <= 12:
        raise ValueError("Invalid year or month")

    _, last_day = calendar.monthrange(year, month)

    start_date = f"{year:04d}-{month:02d}-01"
    end_date = f"{year:04d}-{month:02d}-{last_day:02d}"

    return database.get_total_expenses(
        start_date, end_date
    )


def get_category_spending():
    """Har category ka total spending return karta hai."""
    all_expenses = fetch_all_expenses()
    category_total = {}

    for expense in all_expenses:
        category = expense["category"]

        if category not in category_total:
            category_total[category] = 0.0

        category_total[category] += expense["amount"]

    return category_total


def filter_expenses(
    category=None, start_date=None, end_date=None
):
    """Category aur date range ke basis par expenses filter karta hai."""
    if start_date is not None:
        _validate_date(start_date)

    if end_date is not None:
        _validate_date(end_date)

    if start_date and end_date and start_date > end_date:
        raise ValueError(
            "Start date cannot be after end date"
        )

    if category is not None:
        if not isinstance(category, str):
            raise ValueError("Category must be text")

        category = category.strip().lower() or None

    all_expenses = fetch_all_expenses()
    filtered_list = []

    for item in all_expenses:
        if (
            category
            and item["category"].lower() != category
        ):
            continue

        if start_date and item["date"] < start_date:
            continue

        if end_date and item["date"] > end_date:
            continue

        filtered_list.append(item)

    return filtered_list


if __name__ == "__main__":
    database.create_db()
    print("Expenses logic ready!")
