import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

# Import custom modules (ensure they are in the same directory)
import database
import analytics

# --- Page Configuration ---
st.set_page_config(page_title="Personal Expense Tracker", layout="wide")

# --- Initialize Database ---
# Run this once to ensure tables exist and categories are seeded
database.init_db()

# --- Helper Functions for UI Interaction ---

def add_expense_process(title, amount, category_name, expense_date):
    """Handles the logic to insert a new expense into SQLite."""
    if not title or not amount:
        st.error("Please provide both a title and an amount.")
        return
    conn = None
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        # Get category_id from category name
        cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        result = cursor.fetchone()
        
        if result:
            category_id = result[0]
            # Insert expense
            cursor.execute('''
                INSERT INTO expenses (title, amount, category_id, date)
                VALUES (?, ?, ?, ?)
            ''', (title, amount, category_id, expense_date.strftime('%Y-%m-%d')))
            conn.commit()
            st.success(f"Added: {title} (${float(amount):.2f})")
        else:
            st.error("Error: Category not found.")
            
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def load_data_for_analytics():
    """
    Fetches raw expense data for the analytics functions.
    Returns standard list of dicts, not a DataFrame.
    """
    conn = database.get_db_connection()
    # Use standard sqlite3.Row to get dict-like results easily
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, amount, date FROM expenses")
    rows = cursor.fetchall()
    conn.close()
    
    # Convert sqlite Rows to list of plain dictionaries for analytics functions
    return [dict(row) for row in rows]

def prepare_ai_summary(df):
    """Creates a text summary of spending for the AI prompt."""
    if df.empty:
        return "No expenses recorded yet."

    df_copy = df.copy()
    
    # Clean the amount column so it converts to float safely even if it has '$' or is a string
    df_copy['amount'] = (
        df_copy['amount']
        .astype(str)
        .str.replace('$', '', regex=False)
        .str.strip()
        .astype(float)
    )

    total_spent = df_copy['amount'].sum()
    category_spending = df_copy.groupby('category_name')['amount'].sum()

    summary = f"Total Spend: ${total_spent:.2f}\n"
    summary += "Spending by Category:\n"
    for cat, amt in category_spending.items():
        summary += f"- {cat}: ${amt:.2f}\n"

    return summary

# =========================================
# MAIN UI LAYOUT
# =========================================

st.title("💰 Smart Expense Tracker")
st.markdown("---")

# --- Sidebar: Add New Expense ---
with st.sidebar:
    st.header("Add New Expense")
    
    # Form for better input handling
    with st.form("add_expense_form"):
        exp_title = st.text_input("Title (e.g., Coffee)")
        exp_amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
        
        # Fetch categories dynamically for dropdown
        try:
            cat_conn = database.get_db_connection()
            categories_df = pd.read_sql_query("SELECT name FROM categories", cat_conn)
            cat_conn.close()
            exp_category = st.selectbox("Category", categories_df['name'].tolist())
        except Exception as e:
            st.error(f"Could not load categories: {e}")
            exp_category = st.selectbox("Category", ['Food', 'Transport']) # Fallback

        exp_date = st.date_input("Date", value=date.today())
        
        submitted = st.form_submit_button("Add Expense")
        if submitted:
            add_expense_process(exp_title, exp_amount, exp_category, exp_date)
            # Force refresh of data below by rerunning script
            st.rerun()

# --- Main Area: Data Display ---

# 1. Show All Expenses DataFrame
st.subheader("📋 Expense Register")

# Fetch data joined with categories for the main display
df_display = pd.DataFrame()  # Initialize empty DataFrame
try:
    conn = database.get_db_connection()
    # Use Pandas for nice display
    df_display = pd.read_sql_query("""
        SELECT 
            e.date,
            e.title,
            e.amount,
            c.name as category_name
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        ORDER BY e.date DESC
    """, conn)
    conn.close()
    
    # Format Amount as currency for display
    if not df_display.empty:
        df_display['amount'] = df_display['amount'].apply(lambda x: f"${float(x):.2f}")
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No expenses recorded yet. Use the sidebar to add some!")

except Exception as e:
    st.error(f"Error loading data: {e}")

st.markdown("---")

# 2. Analytics Section (Two Columns)
col1, col2 = st.columns(2)

# --- Left Column: Top Expenses (DSA/Heap) ---
with col1:
    st.subheader("🏆 Top 5 Expenses (Max-Heap)")
    
    # Get raw data list for analytics
    raw_expenses = load_data_for_analytics()
    
    if raw_expenses:
        # Use imported heap function (requesting n=5)
        top_expenses = analytics.get_top_expenses_heap(raw_expenses, n=5)
        
        # Convert result to DataFrame for clean Streamlit display
        top_df = pd.DataFrame(top_expenses)
        # Keep only relevant columns and format
        if not top_df.empty:
            top_df = top_df[['title', 'amount', 'date']]
            top_df['amount'] = top_df['amount'].apply(lambda x: f"${float(x):.2f}")
            st.dataframe(top_df, use_container_width=True, hide_index=True)
    else:
        st.write("Add expenses to see top spenders.")

# --- Right Column: Above Average (SQL) ---
with col2:
    st.subheader("📈 Above Average Expenses")
    
    try:
        # Use imported SQL function from database.py
        above_avg_rows = database.get_above_average_expenses()
        
        if above_avg_rows:
            # Convert sqlite3.Row objects to DataFrame
            above_avg_df = pd.DataFrame(above_avg_rows)
            
            if not above_avg_df.empty:
                # Calculate average for display context
                avg_val = above_avg_df['amount'].mean()
                # Note: the subquery already filtered them, this is just for info
                
                above_avg_df['amount'] = above_avg_df['amount'].apply(lambda x: f"${float(x):.2f}")
                st.dataframe(above_avg_df[['title', 'amount', 'date']], use_container_width=True, hide_index=True)
        else:
            st.write("No expenses exceed the average yet.")
            
    except Exception as e:
        st.error(f"Error loading above average data: {e}")

st.markdown("---")

# --- AI Insights Section ---
st.subheader("🤖 AI Financial Insights")

# Button to trigger AI generation
if st.button("Generate AI Insights based on current month"):
    with st.spinner("Asking Gemini for advice..."):
        # Ensure df_display exists or fall back to loading data directly
        summary_df = df_display if 'df_display' in locals() and df_display is not None else pd.DataFrame()
        summary_text = prepare_ai_summary(summary_df)
        
        # Call imported AI function
        ai_advice = analytics.get_ai_financial_advice(summary_text)
        
        # Display result
        st.markdown("### Gemini's Advice:")
        st.markdown(ai_advice)
        # Display result using st.markdown (expects markdown bullets from Gemini)
        st.markdown("#### Gemini's Advice:")
        st.markdown(ai_advice)

# --- Footer ---
st.markdown("---")
st.caption("Built with Streamlit, SQLite, and Google Gemini.")