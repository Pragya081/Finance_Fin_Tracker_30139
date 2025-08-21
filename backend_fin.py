import psycopg2
from psycopg2 import sql

def get_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname="Fin_Tracker",
            user="postgres",
            password="Pragya@123",
            host="localhost",  # or your host address
            port="5432"
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None

def setup_database():
    """Creates the transactions table if it doesn't exist."""
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id VARCHAR(255) PRIMARY KEY,
                    transaction_date DATE NOT NULL,
                    description TEXT,
                    amount DECIMAL(10, 2) NOT NULL,
                    type VARCHAR(20) CHECK (type IN ('Revenue', 'Expense'))
                );
            """)
            conn.commit()
            print("Database setup complete.")
        except psycopg2.Error as e:
            print(f"Error setting up database: {e}")
        finally:
            cursor.close()
            conn.close()

# --- CRUD Operations ---

def create_transaction(transaction_id, date, description, amount, type):
    """Inserts a new transaction into the database."""
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO transactions (transaction_id, transaction_date, description, amount, type) VALUES (%s, %s, %s, %s, %s)",
                (transaction_id, date, description, amount, type)
            )
            conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"Error creating transaction: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

def read_transactions(transaction_type=None, sort_by=None, sort_order='ASC'):
    """Reads all transactions with optional filtering and sorting."""
    conn = get_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    query = "SELECT transaction_id, transaction_date, description, amount, type FROM transactions"
    params = []
    
    if transaction_type and transaction_type != 'All':
        query += " WHERE type = %s"
        params.append(transaction_type)
    
    if sort_by in ['amount', 'transaction_date']:
        query += f" ORDER BY {sort_by}"
        if sort_order.upper() in ['ASC', 'DESC']:
            query += f" {sort_order.upper()}"
    
    try:
        cursor.execute(query, params)
        transactions = cursor.fetchall()
        return transactions
    except psycopg2.Error as e:
        print(f"Error reading transactions: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def update_transaction(transaction_id, date, description, amount, type):
    """Updates an existing transaction."""
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE transactions SET transaction_date = %s, description = %s, amount = %s, type = %s WHERE transaction_id = %s",
                (date, description, amount, type, transaction_id)
            )
            conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"Error updating transaction: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

def delete_transaction(transaction_id):
    """Deletes a transaction from the database."""
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM transactions WHERE transaction_id = %s",
                (transaction_id,)
            )
            conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"Error deleting transaction: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

# --- Aggregation and Business Insights ---

def get_aggregates():
    """Calculates and returns various financial aggregates."""
    conn = get_connection()
    if not conn:
        return 0, 0, 0, 0, 0, 0, 0, 0

    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) AS total_transactions,
                SUM(CASE WHEN type = 'Revenue' THEN amount ELSE 0 END) AS total_revenue,
                SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END) AS total_expenses,
                SUM(CASE WHEN type = 'Revenue' THEN amount ELSE -amount END) AS net_income,
                MIN(amount) AS min_amount,
                MAX(amount) AS max_amount,
                AVG(amount) AS avg_amount,
                SUM(amount) FILTER (WHERE type = 'Revenue') as total_revenue_sum,
                SUM(amount) FILTER (WHERE type = 'Expense') as total_expense_sum
            FROM transactions;
        """)
        
        result = cursor.fetchone()
        
        # Ensure we handle potential None values
        if result:
            total_transactions, total_revenue, total_expenses, net_income, min_amount, max_amount, avg_amount, _, _ = result
            return (
                total_transactions or 0,
                total_revenue or 0,
                total_expenses or 0,
                net_income or 0,
                min_amount or 0,
                max_amount or 0,
                avg_amount or 0
            )
        else:
            return 0, 0, 0, 0, 0, 0, 0
    except psycopg2.Error as e:
        print(f"Error getting aggregates: {e}")
        return 0, 0, 0, 0, 0, 0, 0
    finally:
        cursor.close()
        conn.close()