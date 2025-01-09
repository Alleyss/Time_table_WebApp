import sqlite3
from sqlite3 import Error

DATABASE_FILE = 'school.db' # Replace with your database name

def create_connection():
    """Create a database connection to a SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        return conn
    except Error as e:
        print(e)
    return conn

def execute_query(query, params=None):
    """Execute an SQL query with optional parameters."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor
    except Error as e:
        print(f"Error executing query: {e}")
        conn.rollback() # rollback the current transaction
    finally:
        if conn:
            conn.close()

def fetch_data(query, params=None):
     """Fetch data from the database based on a query"""
     conn = create_connection()
     cursor = conn.cursor()
     try:
        if params:
            cursor.execute(query,params)
        else:
            cursor.execute(query)
        rows = cursor.fetchall()
        return rows
     except Error as e:
         print(f"Error fetching data: {e}")
     finally:
         if conn:
             conn.close()

def fetch_one(query, params=None):
    """Fetch one row of data from the database based on a query"""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query,params)
        else:
            cursor.execute(query)
        row = cursor.fetchone()
        return row
    except Error as e:
        print(f"Error fetching data: {e}")
    finally:
        if conn:
            conn.close()

# Generic CRUD functions:
def insert_data(table, data):
    """Insert data into the database table"""
    columns = ', '.join(data.keys())
    placeholders = ', '.join('?' for _ in data.values())
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    execute_query(query, tuple(data.values()))


def update_data(table, data, condition, params):
     """Update data in a table based on condition"""
     set_clause = ', '.join(f"{key} = ?" for key in data.keys())
     query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
     params_list = list(data.values())
     params_list.extend(params)
     execute_query(query,tuple(params_list))

def delete_data(table, condition, params):
    """Delete data from table based on condition"""
    query = f"DELETE FROM {table} WHERE {condition}"
    execute_query(query, params)

def get_all_data(table):
    query = f"SELECT * FROM {table}"
    return fetch_data(query)

def get_by_id(table,id_field, id):
    query = f"SELECT * FROM {table} WHERE {id_field} = ?"
    return fetch_one(query, (id,))


if __name__ == '__main__':
    # Test the database connection
    conn = create_connection()
    if conn:
        print("Database connection successful!")
        conn.close()
    else:
        print("Failed to connect to the database.")

    # Example of Insert
    insert_data("schools", {
        "school_name":"My School",
        "academic_year_start":"2024-09-01",
        "academic_year_end":"2025-06-30",
        "session_duration_minutes":45,
        "break_duration_minutes":10
    })

