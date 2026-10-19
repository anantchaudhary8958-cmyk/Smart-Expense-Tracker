# All library files imports
# streamlit , pandas, plotly.express, calendar, datetime
import streamlit as st
import pandas as pd 
import plotly.express as px
import calendar
from datetime import date
import database
import expenses
import budgets

# ----------------------------------------------------------
# 1. PAGE SETTINGS

# Title + Icon + Layout
st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# ----------------------------------------------------------
# 2. CREATE DATABASE (if not exists)

database.create_db()

# Action ke baad success message dikhane ke liye
# session_state message ko rerun ke dauran preserve karta hai
flash_message = st.session_state.pop("flash_message", None)
# Default Categories
CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Education",
    "Travel",
    "Other",
]
# ----------------------------------------------------------
# 2. HELPER FUNCTIONS
# ----------------------------------------------------------
#to match categories 
def match_categories(category):
    from difflib import get_close_matches
    CATEGORIES = [
        "Food",
        "Transport",
        "Shopping",
        "Bills",
        "Entertainment",
        "Health",
        "Education",
        "Travel",
        "Other",
    ]

    if not isinstance(category, str) or not category.strip():
        return "Other"

    category = category.strip()

    # Exact match, ignoring uppercase/lowercase
    for item in CATEGORIES:
        if category.casefold() == item.casefold():
            return item

    # Match close spellings
    matches = get_close_matches(
        category.casefold(),
        [item.casefold() for item in CATEGORIES],
        n=1,
        cutoff=0.75
    )

    if matches:
        return next(
            item for item in CATEGORIES
            if item.casefold() == matches[0]
        )

    return "Other"



def money(amount):
    return f"₹{amount:,.2f}"

def get_all_categories(all_expenses = None , all_budgets = None ):
    if all_expenses is None:
        all_expenses = expenses.fetch_all_expenses()
    if all_budgets is None:
        all_budgets = budgets.get_all_category_budgets()
    
    found = set(CATEGORIES)
    found.update(item["category"] for item in all_expenses)
    found.update(item[0] for item in all_budgets)
    return sorted(list(found))

def expenses_dataFrame(items):
    columns = ["id", "category", "amount", "date", "description"]
    df = pd.DataFrame(items, columns=columns) 
    if not df.empty:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.sort_values(by="date", ascending=False)
    return df

def show_dashboard():
    st.title("💸 Smart Expense Tracker")
    st.caption("Track expenses, understand spending, and keep your monthly budget on target.")

    today = date.today()
    all_items = expenses.fetch_all_expenses()
    df = expenses_dataFrame(all_items)
    monthly_spending = expenses.get_monthly_spending(today.year, today.month)
    total_spending = expenses.get_total_spending()
    budget_rows = budgets.get_all_category_budgets()
    total_monthly_budget = sum(float(row[1]) for row in budget_rows)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Spent this month", money(monthly_spending))
    col2.metric("All-time spending", money(total_spending))
    col3.metric("Recorded expenses", f"{len(all_items)}")
    col4.metric("Combined category budgets", money(total_monthly_budget))

    st.subheader("Recent expenses")
    if df.empty:
        st.info("No expenses yet. Open **Add Expense** in the sidebar to record your first one.")
    else:
        recent = df.head(8).copy()
        recent["date"] = recent["date"].dt.strftime("%Y-%m-%d")
        recent["amount"] = recent["amount"].map(money)
        st.dataframe(recent, use_container_width=True, hide_index=True)

        left, right = st.columns(2)
        category_totals = df.groupby("category", as_index=False)["amount"].sum()
        with left:
            st.subheader("Spending by category")
            fig = px.pie(category_totals, names="category", values="amount", hole=0.45)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            st.subheader("Monthly spending trend")
            monthly = (
                df.dropna(subset=["date"])
                .assign(month=lambda x: x["date"].dt.to_period("M").astype(str))
                .groupby("month", as_index=False)["amount"]
                .sum()
                .tail(6)
            )
            if monthly.empty:
                st.info("Not enough dated expenses to show a trend.")
            else:
                fig = px.bar(monthly, x="month", y="amount", labels={"month": "Month", "amount": "Amount (₹)"})
                st.plotly_chart(fig, use_container_width=True)

    st.subheader("Budget alerts for this month")
    if not budget_rows:
        st.info("No category budgets have been set yet. Open **Budgets** to create one.")
    else:
        alerts = []
        for category, limit in budget_rows:
            try:
                status = budgets.get_budget_status(category, today.year, today.month)
                alerts.append(status)
            except (ValueError, TypeError) as exc:
                st.warning(f"Could not calculate the budget for {category}: {exc}")
        if alerts:
            alert_df = pd.DataFrame(alerts)
            alert_df["budget"] = alert_df["budget"].map(money)
            alert_df["spent"] = alert_df["spent"].map(money)
            alert_df["remaining"] = alert_df["remaining"].map(money)
            alert_df["percentage"] = alert_df["percentage"].map(lambda n: f"{n:.2f}%")
            st.dataframe(alert_df, use_container_width=True, hide_index=True)
            for item in alerts:
                if item["status"] == "Budget Exceeded":
                    st.error(f"{item['category']}: budget exceeded ({money(item['spent'])} spent of {money(item['budget'])}).")
                elif item["status"] == "Warning":
                    st.warning(f"{item['category']}: {item['percentage']:.2f}% of the budget has been used.")
       
def show_add_expense():
    st.title("➕ Add Expense")
    st.caption("Enter the amount, category, date, and an optional note.")

    with st.form("add_expense_form", clear_on_submit=True):
        amount = st.number_input("Amount (₹)", min_value=0.01, value=100.0, step=10.0, format="%.2f")
        category = st.text_input("Category", placeholder="e.g. Food, Travel, Bills")
        expense_date = st.date_input("Expense date", value=date.today())
        description = st.text_area("Description (optional)", placeholder="What was this expense for?")
        submitted = st.form_submit_button("Save expense", type="primary", use_container_width=True)

    if submitted:
        try:
            expense_id = expenses.add_new_expense(
                amount=amount,
                category=match_categories(category),
                date_str=expense_date.strftime("%Y-%m-%d"),
                description=description,
            )
            st.success(f"Expense saved successfully. Expense ID: {expense_id}")
        except (ValueError, TypeError) as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Could not save the expense: {exc}")

  
def show_manage_expenses():
    st.title("🧾 Manage Expenses")
    all_items = expenses.fetch_all_expenses()
    if not all_items:
        st.info("There are no expenses to display yet.")
        return
    
    categories = ["All categories"] + sorted({item["category"] for item in all_items}, key=str.lower)
    chosen_category = st.selectbox("Filter by category", categories)
    filtered = all_items if chosen_category == "All categories" else [item for item in all_items if item["category"] == chosen_category]
    display_df = expenses_dataFrame(filtered)
    if not display_df.empty:
        display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
        display_df["amount"] = display_df["amount"].map(money)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Edit or delete an expense")
    by_id = {item["id"]: item for item in all_items}
    selected_id = st.selectbox(
        "Select expense ID",
        options=list(by_id.keys()),
        format_func=lambda item_id: (
            f"#{item_id} · {by_id[item_id]['date']} · "
            f"{by_id[item_id]['category']} · {money(by_id[item_id]['amount'])}"
        ),
    )
    selected = by_id[selected_id]

    with st.form("edit_expense_form"):
        edit_amount = st.number_input(
            "Amount (₹)", min_value=0.01, value=float(selected["amount"]), step=10.0,
            format="%.2f", key=f"edit_amount_{selected_id}"
        )
        edit_category = st.text_input("Category", value=selected["category"], key=f"edit_category_{selected_id}")
        try:
            initial_date = date.fromisoformat(selected["date"])
        except (TypeError, ValueError):
            initial_date = date.today()
        edit_date = st.date_input("Expense date", value=initial_date, key=f"edit_date_{selected_id}")
        edit_description = st.text_area(
            "Description", value=selected.get("description", ""), key=f"edit_description_{selected_id}"
        )
        update_clicked = st.form_submit_button("Update expense", type="primary")

    if update_clicked:
        try:
            changed = expenses.edit_expenses(
                expense_id=selected_id,
                amount=edit_amount,
                category=match_categories(edit_category),
                date_str=edit_date.strftime("%Y-%m-%d"),
                description=edit_description,
            )
            if changed:
                st.success("Expense updated successfully.")
                st.rerun()
            else:
                st.warning("No expense was updated. Check the selected ID.")
        except (ValueError, TypeError) as exc:
            st.error(str(exc))

    if st.button("🗑️ Delete selected expense", type="secondary"):
        try:
            deleted = expenses.remove_expenses(selected_id)
            if deleted:
                st.success("Expense deleted successfully.")
                st.rerun()
            else:
                st.warning("This expense was not found.")
        except Exception as exc:
            st.error(f"Could not delete the expense: {exc}")

def show_budgets():
    st.title("🎯 Category Budgets")
    st.caption("Set a monthly limit for each category. An alert appears at 80% and when a limit is exceeded.")

    with st.form("set_budget_form", clear_on_submit=True):
        category = st.text_input("Category", placeholder="Use the same category name as your expenses")
        monthly_limit = st.number_input("Monthly budget limit (₹)", min_value=0.01, value=1000.0, step=100.0, format="%.2f")
        submitted = st.form_submit_button("Save budget", type="primary", use_container_width=True)

    if submitted:
        try:
            budgets.set_category_budget(category.lower(), monthly_limit)
            st.success(f"Monthly budget saved for {category.strip()}.")
        except (ValueError, TypeError) as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Could not save the budget: {exc}")

    st.subheader("Current budgets")
    budget_rows = budgets.get_all_category_budgets()
    if not budget_rows:
        st.info("No budgets saved yet.")
        return

    today = date.today()
    rows = []
    for category_name, limit in budget_rows:
        try:
            status = budgets.get_budget_status(match_categories(category_name), today.year, today.month)
            rows.append(status)
        except (ValueError, TypeError) as exc:
            st.warning(f"Could not calculate budget status for {category_name}: {exc}")
            rows.append({
                "category": match_categories(category_name),
                "budget": float(limit),
                "spent": 0.0,
                "remaining": float(limit),
                "percentage": 0.0,
                "status": "Unavailable",
            })

    budget_df = pd.DataFrame(rows)
    budget_df["budget"] = budget_df["budget"].map(money)
    budget_df["spent"] = budget_df["spent"].map(money)
    budget_df["remaining"] = budget_df["remaining"].map(money)
    budget_df["percentage"] = budget_df["percentage"].map(lambda n: f"{n:.2f}%")
    st.dataframe(budget_df, use_container_width=True, hide_index=True)
    
    st.divider()
    st.subheader("🗑️ Delete Budget")

    budget_rows = budgets.get_all_category_budgets()

    if budget_rows:
        selected_category = st.selectbox(
            "Select category budget to delete",
            options=[row[0] for row in budget_rows],
            key="delete_budget_category"
        )

        confirm_delete = st.checkbox(
            f"Confirm deletion of {selected_category} budget",
            key="confirm_delete_budget"
        )

        if st.button("Delete Budget", type="secondary"):
            if not confirm_delete:
                st.warning("Please confirm before deleting.")
            else:
                try:
                    deleted = database.delete_budget(
                        selected_category
                    )

                    if deleted:
                        st.success(
                            f"{selected_category} budget deleted successfully!"
                        )
                        st.rerun()
                    else:
                        st.warning("Budget not found.")

                except Exception as exc:
                    st.error(f"Could not delete budget: {exc}")
    else:
        st.info("No budgets available to delete.")

def show_analytics():
    st.title("📊 Expense Analytics")
    all_items = expenses.fetch_all_expenses()
    if not all_items:
        st.info("Add some expenses first to view analytics.")
        return

    categories = ["All categories"] + sorted({item["category"] for item in all_items}, key=str.lower)
    chosen_category = st.selectbox("Category", categories)
    today = date.today()
    first_day = today.replace(day=1)
    date_cols = st.columns(2)
    with date_cols[0]:
        start_date = st.date_input("From date", value=first_day, key="analytics_start_date")
    with date_cols[1]:
        end_date = st.date_input("To date", value=today, key="analytics_end_date")

    if start_date > end_date:
        st.error("The start date cannot be after the end date.")
        return

    try:
        selected_category = None if chosen_category == "All categories" else chosen_category
        filtered = expenses.filter_expenses(
            category=selected_category,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )
    except ValueError as exc:
        st.error(str(exc))
        return

    df = expenses_dataFrame(filtered)
    total = float(df["amount"].sum()) if not df.empty else 0.0
    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Spending in selected period", money(total))
    metric2.metric("Transactions", len(filtered))
    metric3.metric("Average expense", money(total / len(filtered) if filtered else 0))

    if df.empty:
        st.info("No expenses match these filters.")
        return

    cat_totals = df.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
    left, right = st.columns(2)
    with left:
        st.subheader("Category breakdown")
        st.plotly_chart(px.pie(cat_totals, names="category", values="amount", hole=0.4), use_container_width=True)
    with right:
        st.subheader("Compare categories")
        st.plotly_chart(px.bar(cat_totals, x="category", y="amount", labels={"amount": "Amount (₹)"}), use_container_width=True)

    st.subheader("Filtered transactions")
    shown = df.copy()
    shown["date"] = shown["date"].dt.strftime("%Y-%m-%d")
    shown["amount"] = shown["amount"].map(money)
    st.dataframe(shown, use_container_width=True, hide_index=True)


# ------------------------------ Navigation ------------------------------
st.sidebar.title("💸 Expense Tracker")
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Add Expense", "Manage Expenses", "Budgets", "Analytics"],
)
st.sidebar.caption("Python · Streamlit · SQLite")

try:
    if page == "Dashboard":
        show_dashboard()
    elif page == "Add Expense":
        show_add_expense()
    elif page == "Manage Expenses":
        show_manage_expenses()
    elif page == "Budgets":
        show_budgets()
    elif page == "Analytics":
        show_analytics()
except Exception as exc:
    st.error(f"Something went wrong: {exc}")
    st.caption("Check that database.py, expenses.py, and budgets.py are saved in the same folder as app.py.")


















