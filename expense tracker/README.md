# Expense Tracker with Analytics

An interactive expense management application built using **Python**, **Streamlit**, **SQLite**, and **Google Gemini AI**. This project combines Data Structures & Algorithms (DSA), relational database queries, and AI insights to track personal expenses, evaluate spending trends, and provide budget advice.

---

## 📌 Project Overview
* **Real-World Focus:** Track monthly spending, detect above-average expenditures, rank top transactions, and receive AI-driven budgeting advice.
* **Core DSA Concept:** Max-Heap (`heapq`) for priority-based transaction ranking.
* **Database Tech:** SQLite (relational database handling relational joins, groupings, and subqueries).

---

## 💡 DSA Concept Justification: Max-Heap (`heapq`)

### Why Heap?
To extract the **Top-N Highest Expenses** from a large dataset, sorting the entire list takes $\mathcal{O}(N \log N)$ time. Using a **Max-Heap**, we can extract the top $N$ elements in $\mathcal{O}(N \log K)$ time (where $K$ is the top $N$ limit, e.g., Top 5).

### Why it was the Right Fit:
* **Efficiency:** A heap maintains dynamic ordering efficiently without needing to sort the database records every time a new transaction is logged.
* **Optimal Priority Filtering:** Pushing expenses into a Max-Heap allows $\mathcal{O}(1)$ access to the maximum expense item, making high-value expense tracking lightweight and fast.

---

## 🗄️ Database Architecture & ER Diagram

### Entities & Relationships
1. **`categories` Table**: Stores expense categories (e.g., Food, Travel, Utilities).
   * `id` (INTEGER, Primary Key, Auto Increment)
   * `name` (TEXT, Unique, Not Null)

2. **`expenses` Table**: Stores transaction records linked to a specific category.
   * `id` (INTEGER, Primary Key, Auto Increment)
   * `title` (TEXT, Not Null)
   * `amount` (REAL, Not Null)
   * `date` (TEXT, Not Null)
   * `category_id` (INTEGER, Foreign Key referencing `categories(id)`)

### ER Diagram Description
+------------------+         1 : N         +------------------+
|    categories    | --------------------> |     expenses     |
+------------------+                       +------------------+
| PK  id           |                       | PK  id           |
|     name         |                       |     title        |
+------------------+                       |     amount       |
|     date         |                       +------------------+| FK  category_id  |
+------------------+

## 📊 SQL Query Implementations

### 1. JOIN Query (Expenses with Category Names)
Used to display transaction history along with human-readable category labels.
```sql
SELECT 
    e.id, 
    e.date, 
    e.title, 
    e.amount, 
    c.name AS category_name
FROM expenses e
JOIN categories c ON e.category_id = c.id
ORDER BY e.date DESC;

2. GROUP BY / HAVING Query (Total Spent Per Category > Threshold)
Used to aggregate monthly expenditures and filter out high-spending categories exceeding $100.

SELECT 
    c.name AS category, 
    SUM(e.amount) AS total_spent
FROM expenses e
JOIN categories c ON e.category_id = c.id
GROUP BY c.name
HAVING SUM(e.amount) > 100.00;

3. Subquery (Above Average Expenses)
Used to filter transactions strictly higher than the overall average transaction amount.

SELECT 
    e.title, 
    e.amount, 
    e.date
FROM expenses e
WHERE CAST(e.amount AS FLOAT) > (
    SELECT AVG(CAST(amount AS FLOAT)) 
    FROM expenses
);

🚀 Setup & Installation Instructions
Prerequisites
Python 3.9 or higher

SQLite3 (pre-installed with Python)

1. Set Up Virtual Environment (Optional but Recommended)

python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

2.Install Dependencies

pip install streamlit pandas google-genai

