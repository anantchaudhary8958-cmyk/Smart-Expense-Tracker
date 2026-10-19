Smart Expense Tracker — Project Guide
Project level: Beginner–Intermediate
Estimated duration: 2–3 days
Language: Python
Database: SQLite
Interface: Streamlit

1. Project Overview
Build a Python application that helps users track their expenses, understand their spending habits, and manage monthly budgets.

The application should allow users to add expenses, categorize transactions, calculate monthly spending, and receive alerts when they exceed their budgets.

The main goal is to practice Python logic, functions, data structures, database operations, and basic application development.

2. Features to Build
Essential Features (MVP)
Add an expense with amount, category, date, and description.
View all recorded expenses.
Delete an expense.
Validate user input.
Calculate total expenses.
Calculate monthly spending.
Calculate category-wise spending.
Save expenses permanently in SQLite.
Additional Features
Edit an existing expense.
Filter expenses by date and category.
Set a monthly budget for each category.
Display warnings when spending reaches 80% of a budget.
Display an alert when a budget is exceeded.
Create charts to visualize spending.
Export expenses to CSV.
Finish the essential features before attempting the additional ones.

3. Technologies
Python: Application logic.
SQLite: Permanent storage of expenses and budgets.
Streamlit: Web-based user interface.
Pandas: Data filtering and summaries.
Plotly: Interactive charts.
SQLite is available through Python's built-in sqlite3 module.

4. Project Folder Structure
Create this structure:

smart-expense-tracker/
├── app.py
├── database.py
├── expenses.py
├── budgets.py
├── requirements.txt
├── README.md
└── PROJECT_GUIDE.md
Purpose of Each File
app.py — Streamlit interface and dashboard.
database.py — Database creation and SQL operations.
expenses.py — Adding, editing, deleting, and analyzing expenses.
budgets.py — Budget management and alert calculations.
requirements.txt — External Python dependencies.
README.md — Project description and setup instructions.
PROJECT_GUIDE.md — This development checklist.
5. Database Design
Create an SQLite database named expenses.db automatically when the application starts.

Table 1: expenses
Column	Purpose
id	Unique transaction ID
amount	Expense amount
category	Food, Travel, Shopping, etc.
date	Date of the transaction
description	Optional details
Use an integer primary key for id, a numeric column for amount, and text columns for the category, date, and description.

Table 2: budgets
Column	Purpose
id	Unique budget ID
category	Budget category
monthly_limit	Maximum permitted spending
Make each category unique in the budgets table.

Use SQL parameterized queries instead of inserting user input directly into SQL strings.

6. Day-by-Day Development Plan
Day 1 — Python Logic and Database
Step 1: Create the project folder and virtual environment.

Step 2: Create database.py and write a function to connect to SQLite and create the required tables.

Step 3: Create expenses.py with functions to:

Add an expense.
Retrieve all expenses.
Delete an expense.
Calculate total spending.
Calculate category-wise totals.
Step 4: Test these functions using simple Python scripts or the terminal.

Day 1 completion goal: Expenses can be added, retrieved, deleted, and calculated correctly, with data stored permanently.

Day 2 — Analysis and Budget Logic
Step 1: Add monthly expense calculations.

Step 2: Implement date and category filtering.

Step 3: Create functions to add and retrieve budgets.

Step 4: Calculate the percentage of each budget already spent.

Formula:

Percentage spent = (Amount spent / Monthly budget) × 100

Step 5: Implement alerts:

Below 80%: Normal.
At or above 80% but not over budget: Warning.
Above 100%: Budget exceeded.
Step 6: Test edge cases, including zero amounts, negative amounts, empty descriptions, and months with no expenses.

Day 2 completion goal: All calculations, filters, and budget alerts work correctly.

Day 3 — Streamlit Dashboard
Step 1: Create app.py.

Step 2: Add a form for entering expenses.

Step 3: Display all transactions in a table.

Step 4: Display summary metrics:

Total spending this month.
Number of transactions.
Highest-spending category.
Remaining budget.
Step 5: Add charts for category-wise and monthly spending.

Step 6: Add budget progress indicators and warnings.

Step 7: Test the complete application and write README.md.

Day 3 completion goal: A working application with a usable interface and persistent data storage.

7. Setup Commands
Create and enter the project folder, then create a virtual environment:

python -m venv venv
Activate it on Windows:

venv\Scripts\activate
Install dependencies:

pip install streamlit pandas plotly
Save the external dependencies in requirements.txt:

streamlit
pandas
plotly
SQLite does not need a separate pip installation in a standard Python installation.

8. How to Run the Application
Once app.py is ready, run:

streamlit run app.py
Streamlit will provide a local URL where the application can be opened in your browser.

9. Important Logic to Understand
Before finishing, make sure you understand how to:

Write and call functions.
Use lists and dictionaries.
Handle invalid input with conditions and exceptions.
Work with Python dates.
Use SQL INSERT, SELECT, UPDATE, and DELETE.
Aggregate expenses by category and month.
Compare spending against budgets.
Separate application logic from interface code.
Use functions that return calculated values instead of mixing every calculation directly into the user interface.

10. Testing Checklist
An expense can be added successfully.
Negative amounts and invalid dates are rejected.
Expenses remain after restarting the application.
Deleting an expense updates the totals.
Monthly totals exclude transactions from other months.
Category filters return the correct results.
Budget warnings trigger at the correct threshold.
Empty datasets do not crash the application.
A zero budget does not cause division-by-zero errors.
Charts display the correct data.
11. Rules for Building the Project
Build the logic before the dashboard.
Write small functions instead of one giant function.
Test each feature before moving to the next.
Do not copy code without understanding it.
Keep the project simple enough to finish in three days.
Commit working milestones to Git if you use Git.
Add advanced features only after the essential application works.
12. Definition of Done
The project is complete when a user can add expenses, store them in SQLite, view and filter transactions, see monthly and category-wise summaries, set budgets, and receive correct budget alerts through a Streamlit dashboard.

Final objective: Build a working application while understanding the Python logic behind every major feature.