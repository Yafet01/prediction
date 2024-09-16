import streamlit as st
import pandas as pd

# Function to handle actions
def handle_action(action, row_id, conn):
   ''' cursor = conn.cursor()
    if action == 'Edit':
        st.session_state['page'] = 'Edit Medicine'
        st.session_state['edit_id'] = row_id
        st.rerun()  # This forces the app to rerun and navigate to the edit page
    elif action == 'Delete':
        cursor.execute("DELETE FROM Medicines WHERE rowid=?", (row_id,))
        conn.commit()
        st.success(f"Deleted successfully! (ID: {row_id})")
        st.session_state['page'] = 'Records'
        st.rerun()  # Rerun the app to refresh the records page'''

# Function for the records page
def records(conn):
    st.title("Records")

    if conn:
        cursor = conn.cursor()
        st.subheader("All Records")

        cursor.execute("SELECT rowid, * FROM Medicines")
        medicines = cursor.fetchall()

        columns = ["ID"] + [description[0] for description in cursor.description[1:]]

        if medicines:
            df = pd.DataFrame(medicines, columns=columns)

            entries_to_show = st.number_input('Entries to show', min_value=1, max_value=len(df), value=10)
            df_to_show = df.head(entries_to_show)

            st.dataframe(df_to_show)

            '''selected_id = st.selectbox("Select an entry", df['ID'], index=0)

            if selected_id:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    if st.button("Edit Selected Entry"):
                        handle_action("Edit", selected_id, conn)

                with col2:
                    if st.button("Delete Selected Entry"):
                        handle_action("Delete", selected_id, conn)'''

        else:
            st.write("No records found.")

        """if st.button("Add New Medicine"):
            st.session_state['page'] = 'Add New Medicine'"""
          
    else:
        st.error("Failed to connect to the database.")