import streamlit as st
import sqlite3
from passlib.hash import bcrypt
from predict_page import show_predict_page
from explore_page import show_explore_page
from records import records
from add_medicine_page import show_add_medicine_page
# Import the add_user_page function
from add_user_page import add_user_page

# Function to create a connection to the SQLite database
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        st.error(f"Error connecting to database: {e}")
    return conn

# Function to create the medicines table if it doesn't exist
def create_medicines_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Medicines (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          "Patient Name" TEXT NOT NULL,
                          "Medicine" TEXT,
                          "Disease" TEXT,
                          "Variety" TEXT,
                          "Quantity(Packets)" INTEGER NOT NULL,
                          "Date" DATE NOT NULL,
                          "Season" TEXT
                          )''')
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Error creating Medicine table: {e}")

# Apply custom styles
st.markdown("""
<style>
{}
</style>
""".format(open("styles.css").read()), unsafe_allow_html=True)

# Custom style to hide Streamlit default elements
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Function to authenticate user
def authenticate_user(username, password, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if user:
        hashed_password = user[1]
        if bcrypt.verify(password, hashed_password):
            st.session_state["authenticated"] = True
            st.session_state["user"] = username
            st.session_state["login_error"] = ""
            return True
    st.session_state["authenticated"] = False
    st.session_state["login_error"] = "Invalid username or password."
    return False

# Function to log out
def logout():
    st.session_state["authenticated"] = False
    st.session_state["user"] = ""
    st.session_state.pop("page", None)
    st.session_state.pop("records_page", None)
    st.session_state.pop("section", None)

# Main function
def main():
    st.title('Drug Prescription and Disease Dataset Analysis')

    # Connect to SQLite databases
    conn = create_connection("users.db")
    medicine_conn = create_connection("Historical_Data_Medicine.db")

    # Initialize session state variables
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["user"] = ""
        st.session_state["login_error"] = ""
        st.session_state["section"] = "General"
        st.session_state["page"] = "Predict"
        st.session_state["records_page"] = "View Records"  # Default record page

    if not st.session_state["authenticated"]:
        st.image(r"C:\Users\tedya\OneDrive\Pictures\Cyberpunk 2077\photomode_28092023_224143.png", use_column_width=True)
        st.sidebar.title("Login")

        with st.sidebar.form(key='login_form'):
            username_input = st.text_input("Username", key="username_input")
            password_input = st.text_input("Password", type="password", key="password_input")

            if st.form_submit_button("Login"):
                if authenticate_user(username_input, password_input, conn):
                    st.rerun()

        if st.session_state["login_error"]:
            st.sidebar.error(st.session_state["login_error"])

    else:
        st.sidebar.title(f"Welcome, {st.session_state['user']}!")

        if medicine_conn is not None:
            create_medicines_table(medicine_conn)
        else:
            st.error("Failed to connect to the Medicine database.")

        # Sidebar navigation
        section_selection = st.sidebar.selectbox(
            "Select Section",
            ["General", "Records"],
            key="section_selectbox"
        )
        st.session_state["section"] = section_selection

        if section_selection == "General":
            page_selection = st.sidebar.selectbox(
                "Select Page",
                ["Predict", "Explore"],
                key="page_selectbox"
            )
            st.session_state["page"] = page_selection
            st.session_state["records_page"] = None

            # Display the selected page
            if st.session_state["page"] == "Predict":
                show_predict_page()
            elif st.session_state["page"] == "Explore":
                show_explore_page()
            else:
                st.error("Invalid page selection.")

        elif section_selection == "Records":
            # Records Menu
            records_menu = st.sidebar.selectbox(
                "Records Menu",
                ["View Records", "Add New Medicine", "Add Users"],
                key="records_menu_selectbox"
            )
            st.session_state["page"] = "Records"
            st.session_state["records_page"] = records_menu

            # Handle records menu
            if st.session_state["records_page"] == "View Records":
                records(medicine_conn)
            elif st.session_state["records_page"] == "Add New Medicine":
                show_add_medicine_page(medicine_conn)
            elif st.session_state["records_page"] == "Add Users":
                add_user_page(conn)  # Function to add new users

        logout_button = st.sidebar.button("Log Out", key="logout_button")

        if logout_button:
            logout()
            st.rerun()

    # Close database connections
    if medicine_conn:
        medicine_conn.close()
    if conn:
        conn.close()

if __name__ == '__main__':
    main()