import streamlit as st
import pandas as pd
from backend_fin import (
    setup_database,
    create_transaction,
    read_transactions,
    update_transaction,
    delete_transaction,
    get_aggregates
)

# --- App Setup ---
st.set_page_config(page_title="Finance: Revenue & Expense Tracker", layout="wide")
st.title("💰 Finance: Revenue & Expense Tracker")

# Ensure the database table is created on app startup
setup_database()

# --- Helper Functions for Display ---
def display_aggregates_and_insights():
    st.header("Financial Overview")
    total_transactions, total_revenue, total_expenses, net_income, min_amount, max_amount, avg_amount = get_aggregates()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Transactions", f"{total_transactions:,}")
    with col2:
        st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
    with col3:
        st.metric("Total Expenses", f"₹{total_expenses:,.2f}")
    with col4:
        st.metric("Net Income", f"₹{net_income:,.2f}")

    st.subheader("Key Business Insights")
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    with insight_col1:
        st.metric("Minimum Transaction Amount", f"₹{min_amount:,.2f}")
    with insight_col2:
        st.metric("Maximum Transaction Amount", f"₹{max_amount:,.2f}")
    with insight_col3:
        st.metric("Average Transaction Amount", f"₹{avg_amount:,.2f}")

# --- Frontend Sections (CRUD) ---

# Section for Creating a new transaction
st.header("Create New Transaction")
with st.form("create_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        transaction_id = st.text_input("Transaction ID", help="Must be a unique identifier.")
        date = st.date_input("Transaction Date")
        description = st.text_area("Description")
    with col2:
        amount = st.number_input("Amount", min_value=0.01, format="%.2f")
        transaction_type = st.selectbox("Type", ["Revenue", "Expense"])
    
    submitted = st.form_submit_button("Add Transaction")
    if submitted:
        if transaction_id and date and amount and transaction_type:
            if create_transaction(transaction_id, date, description, amount, transaction_type):
                st.success("Transaction added successfully!")
            else:
                st.error("Error adding transaction. Please check the Transaction ID for uniqueness.")
        else:
            st.error("Please fill in all the required fields.")

# Separator
st.markdown("---")
display_aggregates_and_insights()
st.markdown("---")

# Section for Reading, Filtering, and Sorting
st.header("View All Transactions")
col1, col2, col3 = st.columns(3)
with col1:
    filter_type = st.selectbox("Filter by Type", ["All", "Revenue", "Expense"])
with col2:
    sort_by = st.selectbox("Sort By", ["transaction_date", "amount"])
with col3:
    sort_order = st.selectbox("Sort Order", ["ASC", "DESC"])

transactions = read_transactions(filter_type, sort_by, sort_order)
if transactions:
    df = pd.DataFrame(
        transactions,
        columns=["Transaction ID", "Date", "Description", "Amount", "Type"]
    )
    st.dataframe(df, use_container_width=True)
else:
    st.info("No transactions found.")

# Section for Updating and Deleting transactions
st.header("Update or Delete Transaction")
transaction_ids = [t[0] for t in read_transactions()]
selected_id = st.selectbox("Select Transaction ID to Edit", options=transaction_ids)

if selected_id:
    # Fetch details for the selected transaction
    selected_transaction = next((t for t in transactions if t[0] == selected_id), None)
    if selected_transaction:
        with st.form("update_delete_form"):
            update_col1, update_col2 = st.columns(2)
            with update_col1:
                new_date = st.date_input("New Transaction Date", value=selected_transaction[1])
                new_description = st.text_area("New Description", value=selected_transaction[2])
            with update_col2:
                new_amount = st.number_input("New Amount", min_value=0.01, value=float(selected_transaction[3]), format="%.2f")
                new_type = st.selectbox("New Type", ["Revenue", "Expense"], index=["Revenue", "Expense"].index(selected_transaction[4]))
            
            update_btn, delete_btn = st.columns(2)
            with update_btn:
                update_submitted = st.form_submit_button("Update Transaction")
                if update_submitted:
                    if update_transaction(selected_id, new_date, new_description, new_amount, new_type):
                        st.success(f"Transaction {selected_id} updated successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Error updating transaction.")
            with delete_btn:
                delete_submitted = st.form_submit_button("Delete Transaction")
                if delete_submitted:
                    if delete_transaction(selected_id):
                        st.success(f"Transaction {selected_id} deleted successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Error deleting transaction.")