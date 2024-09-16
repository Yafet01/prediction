import sqlite3
from passlib.hash import bcrypt

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Connection to SQLite DB successful")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")
    return conn

def create_table(conn):
    """Create a table from the create_table_sql statement."""
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    );
    """
    try:
        c = conn.cursor()
        c.execute(create_users_table)
        print("Table 'users' created successfully")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")

def add_user(conn, username, password):
    """Add a new user into the users table."""
    sql = ''' INSERT INTO users(username, password)
              VALUES(?, ?) '''
    hashed_password = bcrypt.hash(password)
    cur = conn.cursor()
    cur.execute(sql, (username, hashed_password))
    conn.commit()
    print(f"User '{username}' added successfully")

def setup_database():
    """Setup database and add default user."""
    conn = create_connection("users.db")
    if conn is not None:
        create_table(conn)
        add_user(conn, "Tedros", "pass123")
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    setup_database()
