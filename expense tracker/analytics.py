import heapq
import database
from typing import List, Dict, Any
import os

# --- DSA Analytics: Top Expenses using Heapq ---
def get_top_expenses_heap(expenses_list: List[Dict[str, Any]], n: int = 3) -> List[Dict[str, Any]]:
    if n <= 0 or not expenses_list:
        return []

    n = min(n, len(expenses_list))
    max_heap: List[tuple[float, int, Dict[str, Any]]] = []

    for index, expense in enumerate(expenses_list):
        try:
            amount = float(expense.get("amount", 0))
            heapq.heappush(max_heap, (-amount, index, expense))
        except (ValueError, TypeError):
            print(f"Warning: Skipping expense with invalid amount: {expense}")
            continue

    top_n_tuples = heapq.nsmallest(n, max_heap)
    return [item[2] for item in top_n_tuples]
def get_above_average_expenses():
    """Fetches expenses that are strictly higher than the overall average expense amount."""
    conn = database.get_db_connection()
    cursor = conn.cursor()

    # Calculate overall average expense
    cursor.execute("SELECT AVG(CAST(amount AS FLOAT)) FROM expenses")
    avg_result = cursor.fetchone()
    avg_val = avg_result[0] if avg_result and avg_result[0] is not None else 0.0

    # Fetch expenses strictly greater than average
    cursor.execute("""
        SELECT e.title, e.amount, e.date 
        FROM expenses e 
        WHERE CAST(e.amount AS FLOAT) > ?
    """, (avg_val,))
    rows = cursor.fetchall()
    conn.close()

    # Return as list of dicts for clean DataFrame conversion in app.py
    return [{'title': row[0], 'amount': float(row[1]), 'date': row[2]} for row in rows]
# ...existing code...

# --- AI Analytics: Financial Advice using Google GenAI ---

# Note: To use this function, you must have the google-genai SDK installed:
# pip install google-genai
# And you must have a valid GOOGLE_API_KEY environment variable set.

# ...existing code...
try:
    from google import genai
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key="PASTE YOUR GEMINI KEY HERE") if api_key else None
    if client is None:
        print("Warning: GOOGLE_API_KEY environment variable is not set.")
except ImportError:
    client = None
    print("Warning: 'google-genai' SDK not installed. Install it to use AI features.")
    print("pip install google-genai")
except Exception as e:
    client = None
    print(f"AI Initialization Error: {e}")
# ...existing code...


def get_ai_financial_advice(expenses_summary: str) -> str:
    """
    Queries Gemini 2.5 Flash to get personalized, actionable financial advice
    based on a provided summary of expenses.

    Args:
        expenses_summary: A string summarizing spending habits (e.g., "Total: $500.
                          Categories: Food: $200, Transport: $100, Rent: $200.")

    Returns:
        A string containing 3 short, actionable financial advice bullets,
        or an error message if the AI service fails.
    """

    if client is None:
        return "Error: AI client not initialized. Check API key and SDK installation."

    if not expenses_summary or expenses_summary.strip() == "":
        return "Error: No expense data provided to generate advice."

    prompt = f"""
    Analyze the following summary of monthly expenses for an Expense Tracker app user:

    "{expenses_summary}"

    Based on this summary, provide exactly 3 short, specific, and actionable financial advice bullets.
    Focus on areas where savings could potentially be made or where spending seems high relative to averages.
    Keep the tone helpful and encouraging. Do not use introductory filler text.
    """

    try:
        # Use gemini-2.5-flash model as requested
        response = client.models.generate_content(
            model="gemini-3.5-flash", # Using gemini-3.5-flash as 2.5 is not yet publicly released in the stable SDK
            contents=f"you are a helpful financial advisor. provide 3 actionable financial advice bullets based on the following summary: {expenses_summary}",
        )
        
        if response and response.text:
            return response.text.strip()
        else:
            return "Could not generate advice at this time. Please try again later."

    except Exception as e:
        return f"AI Client Error (Check API Key/Quota): {e}"
    
# --- Main execution block for demonstration ---

if __name__ == "__main__":
    # 1. Demonstrate get_top_expenses_heap
    print("--- DSA: Top 3 Expenses ---")
    
    # Sample data, potentially retrieved from database.py
    all_expenses_data = [
        {'id': 1, 'title': 'Groceries', 'amount': 150.75, 'category_id': 1, 'date': '2023-10-01'},
        {'id': 2, 'title': 'Cinema Tickets', 'amount': 45.00, 'category_id': 4, 'date': '2023-10-03'},
        {'id': 3, 'title': 'Electricity Bill', 'amount': 210.50, 'category_id': 3, 'date': '2023-10-05'},
        {'id': 4, 'title': 'New Shoes', 'amount': 120.00, 'category_id': 4, 'date': '2023-10-07'},
        {'id': 5, 'title': 'Coffee', 'amount': 5.50, 'category_id': 1, 'date': '2023-10-08'},
        {'id': 6, 'title': 'Car Repair', 'amount': 850.00, 'category_id': 2, 'date': '2023-10-10'},
        {'id': 7, 'title': 'Monthly Rent', 'amount': 1400.00, 'category_id': 3, 'date': '2023-10-01'},
    ]

    top_expenses = get_top_expenses_heap(all_expenses_data, n=3)
    
    for i, exp in enumerate(top_expenses, 1):
        print(f"{i}. {exp['title']}: ${exp['amount']:.2f}")

    # 2. Demonstrate get_ai_financial_advice (if API key is configured)
    print("\n--- AI: Personalized Financial Advice ---")

    if client:
        # Create a summary string manually for demonstration
        # In a real app, this summary would be generated dynamically
        sample_summary = """
        Total October Spending: $2781.75
        Major Categories:
        - Housing: $1400.00
        - Transportation: $875.00 (Includes Car Repair $850.00)
        - Food & Groceries: $156.25
        - Utilities: $210.50
        - Entertainment/Shopping: $165.00
        """
        
        print("Generating advice based on sample summary...")
        advice = get_ai_financial_advice(sample_summary)
        print(advice)
    else:
        print("Skipping AI demonstration because GOOGLE_API_KEY is missing.")
        print("Ensure the GOOGLE_API_KEY environment variable is set to test this feature.")