import sqlite3
import os

# Define the database file name
DB_NAME = "expense_tracker.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    # Row objects allow us to access columns by name (e.g., row['title'])
    # instead of by index (e.g., row[1]).
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database by creating the necessary tables
    and populating them with default categories if they don't exist.
    """
    # Check if database file already exists to know if we need to seed data
    db_exists = os.path.exists(DB_NAME)
    
    conn = get_db_connection()
    cursor = conn.cursor()

    if not db_exists:
        print("Database not found. Creating tables and seeding data...")
    else:
        print("Database found. Ensuring tables exist...")

    # 1. Create 'categories' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # 2. Create 'expenses' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category_id INTEGER,
            date TEXT NOT NULL,  
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    # Seed default categories only if we just created the database
    if not db_exists:
        default_categories = [('Food',), ('Transport',), ('Bills',), ('Shopping',)]
        cursor.executemany('''
            INSERT OR IGNORE INTO categories (name) VALUES (?)
        ''', default_categories)
        print("Default categories seeded.")

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# ==========================================
# Specific Query Functions
# ==========================================

def get_expenses_with_categories():
    """
    Fetches all expenses joined with their category names using INNER JOIN.
    Returns a list of Row objects.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Perform an INNER JOIN to combine expense data with category names
    query = '''
        SELECT 
            e.id, 
            e.title, 
            e.amount, 
            e.date, 
            c.name AS category_name
        FROM expenses e
        INNER JOIN categories c ON e.category_id = c.id
        ORDER BY e.date DESC
    '''
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_high_spending_categories(threshold=1000):
    """
    Finds categories where the total spending exceeds a specific threshold.
    Uses GROUP BY and HAVING.
    Returns a list of Row objects (category_name, total_spent).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Group expenses by category, sum amounts, and filter using HAVING
    query = '''
        SELECT 
            c.name AS category_name,
            SUM(e.amount) AS total_spent
        FROM categories c
        JOIN expenses e ON c.id = e.category_id
        GROUP BY c.id, c.name
        HAVING total_spent > ?
        ORDER BY total_spent DESC
    '''
    
    cursor.execute(query, (threshold,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_above_average_expenses():
    """
    Fetches individual expenses that are higher than the average expense amount.
    Uses a subquery.
    Returns a list of Row objects.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Select expenses where amount is greater than the result of a subquery
    # that calculates the average amount across the whole table.
    query = '''
        SELECT 
            id, 
            title, 
            amount, 
            date
        FROM expenses
        WHERE amount > (SELECT AVG(amount) FROM expenses)
        ORDER BY amount DESC
    '''
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

# ==========================================
# Helper function to add dummy data for testing
# ==========================================
def add_dummy_data():
    """Adds sample expenses to test the queries."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sample_expenses = [
        ('Lunch', 12.50, 1, '2023-10-27'),
        ('Uber ride', 25.00, 2, '2023-10-27'),
        ('Electricity Bill', 150.00, 3, '2023-10-10'),
        ('New Shoes', 120.00, 4, '2023-10-28'),
        ('Groceries', 80.00, 1, '2023-10-29'),
        ('Laptop', 1200.00, 4, '2023-10-01'), # High value item
        ('Rent', 1400.00, 3, '2023-11-01'),     # High value item
        ('Coffee', 5.50, 1, '2023-10-30')
    ]
    
    try:
        cursor.executemany('''
            INSERT INTO expenses (title, amount, category_id, date)
            VALUES (?, ?, ?, ?)
        ''', sample_expenses)
        conn.commit()
        print("Dummy expense data added.")
    except sqlite3.IntegrityError:
        print("Dummy data might already exist.")
        
    conn.close()

# ==========================================
# Main execution block (for demonstration)
# ==========================================
if __name__ == "__main__":
    # 1. Initialize the database and seed categories
    init_db()

    # 2. Add dummy data (only if running this script directly)
    # We wrap this in a check to prevent duplicate data if run multiple times
    try:
        check_conn = get_db_connection()
        cursor = check_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM expenses")
        if cursor.fetchone()[0] == 0:
             add_dummy_data()
        check_conn.close()
    except sqlite3.OperationalError:
        # Table might not exist if init_db failed
        pass

    # 3. Run and Print Query 1: Expenses with Category Names
    print("\n--- Query 1: All Expenses (Joined with Categories) ---")
    expenses = get_expenses_with_categories()
    for exp in expenses:
        print(f"ID: {exp['id']} | Title: {exp['title']} | Amount: ${exp['amount']:.2f} | Date: {exp['date']} | Category: {exp['category_name']}")

    # 4. Run and Print Query 2: High Spending Categories (> $1000)
    print("\n--- Query 2: Categories with total spending > $1000 ---")
    high_spending = get_high_spending_categories(1000)
    for cat in high_spending:
        print(f"Category: {cat['category_name']} | Total Spent: ${cat['total_spent']:.2f}")

    # 5. Run and Print Query 3: Above Average Expenses
    print("\n--- Query 3: Expenses above the average amount ---")
    above_avg = get_above_average_expenses()
    for exp in above_avg:
        print(f"ID: {exp['id']} | Title: {exp['title']} | Amount: ${exp['amount']:.2f} | Date: {exp['date']}")