
import database
import expenses


def set_category_budget(category, monthly_limit):
    # Check karo ki category khaali to nahi hai
    if not isinstance(category, str) or not category.strip():
        raise ValueError("Category cannot be empty")

    # Budget ko number mein convert karo
    try:
        monthly_limit = float(monthly_limit)
    except (ValueError, TypeError):
        raise ValueError("Enter a valid budget amount") from None

    # Budget zero ya negative nahi hona chahiye
    if monthly_limit <= 0:
        raise ValueError("Budget must be greater than zero")

    # Database mein budget save ya update karo
    return database.set_budget(
        category.strip(), monthly_limit
    )


def get_category_budget(category):
    # Kisi category ka budget database se nikalo
    return database.get_budget(category.strip())


def get_all_category_budgets():
    # Sabhi categories ke budgets ki list return karo
    return database.get_all_budgets()


def get_budget_status(category, year, month):
    # Category ka monthly budget nikalo
    budget = get_category_budget(category)

    # Agar budget set nahi hai, to error do
    if budget is None:
        raise ValueError(
            f"No budget set for category: {category}"
        )

    # Usi category ka monthly spending calculate karo
    monthly_expenses = expenses.filter_expenses(
        category=category,
        start_date=f"{int(year):04d}-{int(month):02d}-01",
        end_date=(
            f"{int(year):04d}-{int(month):02d}-"
            f"{__import__('calendar').monthrange(int(year), int(month))[1]:02d}"
        ),
    )

    # Filter kiye gaye expenses ka total nikalo
    spent = sum(item["amount"] for item in monthly_expenses)

    # Kitna budget use hua, percentage mein calculate karo
    percentage = (spent / budget) * 100

    # Bacha hua budget calculate karo
    remaining = budget - spent

    # Spending ke hisaab se alert tayyar karo
    if percentage > 100:
        status = "Budget Exceeded"
    elif percentage >= 80:
        status = "Warning"
    else:
        status = "Normal"

    # Saare results dictionary mein return karo
    return {
        "category": category,
        "budget": budget,
        "spent": spent,
        "remaining": remaining,
        "percentage": round(percentage, 2),
        "status": status,
    }


if __name__ == "__main__":
    # Database aur tables create karna ensure karo
    database.create_db()

    print("Budget management logic ready!")
