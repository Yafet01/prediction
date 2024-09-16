import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

def edit_page(conn):
    st.title("Edit Medicine Entry")

    # Retrieve the edit_id from session state
    edit_id = st.session_state.get('edit_id', None)

    if not edit_id:
        st.error("No medicine entry selected for editing.")
        return

    cursor = conn.cursor()

    try:
        # Fetch the record to be edited
        cursor.execute("SELECT * FROM Medicines WHERE rowid=?", (edit_id,))
        record = cursor.fetchone()

        if not record:
            st.error("Medicine entry not found.")
            return

        # Retrieve column names
        column_names = [description[0] for description in cursor.description]
        
        # Extract current values based on column names
        data = dict(zip(column_names, record))
        patient_name = data.get("Patient Name")
        medicine_name = data.get("Medicine")
        disease = data.get("Disease")
        variety = data.get("Variety")
        quantity = data.get("Quantity(Packets)")
        date = pd.to_datetime(data.get("Date"))  # Ensure date is a datetime object
        season = data.get("Season")

        # Convert date to MM/DD/YYYY format for display
        formatted_date = date.strftime('%m/%d/%Y')

        # Form to edit the medicine entry
        with st.form(key='edit_medicine_form'):
            st.subheader("Edit Record Details")

            patient_name = st.text_input("Patient Name", value=patient_name)
            medicine_name = st.text_input("Medicine", value=medicine_name)
            disease = st.text_input("Disease", value=disease)
            variety = st.text_input("Variety", value=variety)
            quantity = st.number_input("Quantity (Packets)", min_value=1, step=1, value=int(quantity))
            date = st.date_input("Date", value=date, format='MM/DD/YYYY')
            season = st.selectbox("Season", ["Wet", "Dry"], index=0 if season == "Wet" else 1)

            # Submit button
            submit_button = st.form_submit_button(label="Update Medicine")

            if submit_button:
                try:
                    # Convert date back to database format (MM-DD-YYYY)
                    date_str = date.strftime('%m/%d/%Y')

                    # Update the medicine entry in the database
                    cursor.execute('''
                        UPDATE Medicines
                        SET "Patient Name" = ?, "Medicine" = ?, "Disease" = ?, "Variety" = ?, 
                            "Quantity(Packets)" = ?, "Date" = ?, "Season" = ?
                        WHERE rowid = ?
                    ''', (patient_name, medicine_name, disease, variety, quantity, date_str, season, edit_id))
                    conn.commit()

                    st.success("Medicine entry updated successfully!")

                    # Redirect to the records page after update
                    st.session_state['page'] = 'Records'
                    st.session_state.pop('edit_id', None)  # Clear edit_id from session state
                    st.experimental_rerun()

                except sqlite3.Error as e:
                    st.error(f"An error occurred while updating the entry: {e}")

    except sqlite3.Error as e:
        st.error(f"An error occurred while fetching the entry: {e}")
