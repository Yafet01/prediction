import streamlit as st
import sqlite3
from passlib.hash import bcrypt

# Function to create the users table if it doesn't exist
def create_users_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          username TEXT NOT NULL UNIQUE,
                          password TEXT NOT NULL
                          )''')
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Error creating users table: {e}")

# Function to add a new user
def add_user(conn, username, password):
    try:
        cursor = conn.cursor()
        hashed_password = bcrypt.hash(password)  # Hash the password before storing
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        st.success(f"User {username} added successfully!")
    except sqlite3.IntegrityError:
        st.error(f"Username {username} is already taken. Please choose a different one.")
    except sqlite3.Error as e:
        st.error(f"Error adding user: {e}")

# Function to display the Add Users page
def add_user_page(conn):
    st.header("Add New User")

    # Create users table if it doesn't exist
    create_users_table(conn)

    # Form to input new user details
    with st.form(key="add_user_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.form_submit_button("Add User"):
            if password != confirm_password:
                st.error("Passwords do not match. Please try again.")
            elif len(username) == 0 or len(password) == 0:
                st.error("Username and password cannot be empty.")
            else:
                add_user(conn, username, password)

