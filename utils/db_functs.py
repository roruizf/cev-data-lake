import sqlite3
import os
import pandas as pd

def create_database(db_file_path: str) -> None:
    """
    Check if the SQLite database file exists, and create it if it doesn't.

    Parameters:
    - db_file_path (str): The path to the SQLite database file.
    """

    # Check if the database file exists
    if not os.path.exists(db_file_path):
        # If the file doesn't exist, create it
        # Create a connection to the database
        conn = sqlite3.connect(db_file_path)
        conn.close()  # Close the connection
        print(f"Database file '{db_file_path}' created successfully.")
    else:
        # If the file already exists, print a message
        print(f"Database file '{db_file_path}' already exists.")


def create_tables(db_file_path: str, table_queries: dict) -> None:
    """
    Create the specified tables in the SQLite database file if they do not already exist.

    Parameters:
    - db_file_path (str): The path to the SQLite database file.
    - table_queries (dict): A dictionary mapping table names to their creation queries.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()

        for table_name, query in table_queries.items():
            # Check if the table exists
            cursor.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            existing_table = cursor.fetchone()

            if existing_table is None:
                # Table does not exist, create it
                cursor.execute(query)
                print(f"Table '{table_name}' created successfully.")
            else:
                # Table already exists, print a message
                print(f"Table '{table_name}' already exists.")

    except sqlite3.Error as e:
        # Handle SQLite errors
        print(f"SQLite error: {e}")

    finally:
        # Close the database connection
        if conn:
            conn.close()


def fill_table_from_dataframe(db_file_path: str, table_name: str, df: pd.DataFrame) -> None:
    """
    Fill a specified table in the SQLite database with data from a pandas DataFrame.

    Parameters:
    - db_file_path (str): The path to the SQLite database file.
    - table_name (str): The name of the table to fill with data.
    - df (pd.DataFrame): DataFrame containing data for the table.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file_path)
        
        # Fill the specified table with data from the DataFrame
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"Table '{table_name}' filled successfully.")

    except sqlite3.Error as e:
        # Handle SQLite errors
        print(f"SQLite error: {e}")

    finally:
        # Close the database connection
        if conn:
            conn.close()

def create_dataframe_from_query(db_file_path: str, query: str) -> pd.DataFrame:
    """
    Create a pandas DataFrame from the results of a SQL query.

    Parameters:
    - db_file_path (str): The path to the SQLite database file.
    - query (str): The SQL query to execute.

    Returns:
    - pd.DataFrame: DataFrame containing the results of the query.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file_path)

        # Execute the query and fetch results into a DataFrame
        df = pd.read_sql_query(query, conn)

        return df

    except sqlite3.Error as e:
        # Handle SQLite errors
        print(f"SQLite error: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

    finally:
        # Close the database connection
        if conn:
            conn.close()

def insert_unique_rows_from_dataframe(db_file_path: str, table_name: str, df: pd.DataFrame, unique_columns: list) -> None:
    """
    Insert rows into a specified table in the SQLite database from a pandas DataFrame,
    ensuring that each row is unique based on the specified unique columns.

    Parameters:
    - db_file_path (str): The path to the SQLite database file.
    - table_name (str): The name of the table to insert rows into.
    - df (pd.DataFrame): DataFrame containing data for the table.
    - unique_columns (list): List of column names that should be unique.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()

        for index, row in df.iterrows():
            # Check if the row already exists based on the unique columns
            unique_values = tuple(row[col] for col in unique_columns)
            placeholders = ', '.join(['?'] * len(unique_columns))
            check_query = f"SELECT 1 FROM {table_name} WHERE " + ' AND '.join([f"{col} = ?" for col in unique_columns])
            cursor.execute(check_query, unique_values)
            exists = cursor.fetchone()

            if not exists:
                # Row does not exist, insert it
                insert_query = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({', '.join(['?' for _ in range(len(df.columns))])})"
                cursor.execute(insert_query, tuple(row))
            else:
                print(f"Duplicate row found for unique columns {unique_columns}: {unique_values}. Skipping insertion.")

        # Commit the changes
        conn.commit()
        print(f"Rows inserted into table '{table_name}' successfully.")

    except sqlite3.Error as e:
        # Handle SQLite errors
        print(f"SQLite error: {e}")

    finally:
        # Close the database connection
        if conn:
            conn.close()