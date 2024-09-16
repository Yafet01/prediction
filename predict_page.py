import pandas as pd
import numpy as np
import pickle
import streamlit as st
import altair as alt
import joblib

# Load the model and feature columns
def load_model(model_path):
    try:
        with open(model_path, "rb") as file:
            return joblib.load(file)
    except FileNotFoundError:
        st.error(f"Model file not found at: {model_path}")
        return None

def load_feature_columns(feature_columns_path):
    try:
        with open(feature_columns_path, "rb") as file:
            return joblib.load(file)
    except FileNotFoundError:
        st.error(f"Feature columns file not found at: {feature_columns_path}")
        return None

# Preprocess input for prediction
def preprocess_input(Year, Month, Medicines, Season, feature_columns, df):
    month_map = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }
    month_numeric = month_map.get(Month, 0)  # Default to 0 if month is invalid

    input_data = []
    for medicine in Medicines:
        # Get the most recent quantity data for the selected medicine
        medicine_df = df[df['Medicine'] == medicine]
        prev_quantity = medicine_df['Quantity(Packets)'].shift(1).fillna(0).values[-1]
        
        # Prepare the input features in the correct order
        features = [
            Year,
            month_numeric,
            prev_quantity
        ]
        
        # One-hot encode the Season input
        season_one_hot = [0] * (len(feature_columns) - 3)  # Adjust for number of one-hot encoded season columns
        
        if f'Season_{Season}' in feature_columns:
            season_one_hot[feature_columns.index(f'Season_{Season}') - 3] = 1
        
        features.extend(season_one_hot)
        
        input_data.append(features)
    
    return np.array(input_data)


def show_predict_page(model_path='Model/best_rf_model.pkl', feature_columns_path='Model/feature_columns.pkl', dataset_path="Model/Historical_Data_2021_Jan_2024.csv"):
    st.title('Medicine Quantity Prediction')
    st.write('Please fill in the following details to predict the quantity of medicine needed.')

    # Load the dataset and feature columns
    df = pd.read_csv(dataset_path)
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    df['YearMonth'] = df['Date'].dt.to_period('M')

    unique_medicines = df['Medicine'].unique()
    unique_diseases = df['Disease'].unique()
    
    feature_columns = load_feature_columns(feature_columns_path)
    if feature_columns is None:
        return

    model = load_model(model_path)
    if model is None:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        Year = st.number_input('Year', min_value=2024)
    
    with col2:
        Month = st.selectbox('Month', options=[
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])
    
    Season = st.radio('Season', ('Wet', 'Dry'))
    Medicines = st.multiselect("Select Medicines", unique_medicines)

    if st.button("Submit"):
        if not Medicines:
            st.warning("Please select at least one medicine before submitting.")
            return

        table_data = []
        for medicine in Medicines:
            diseases = df[df['Medicine'] == medicine]['Disease'].unique()
            
            for disease in diseases:
                input_data = preprocess_input(Year, Month, [medicine], Season, feature_columns, df)
                
                if input_data is None:
                    return

                # Predict quantity for this medicine-disease combination
                predictions = model.predict(input_data)
                table_data.append({
                    "Month": Month,
                    "Medicine": medicine,
                    "Disease": disease,
                    "Predicted Quantity": int(round(predictions[0]))
                })
    
        df_result = pd.DataFrame(table_data)
        # Group by Month, Medicine, and Disease to aggregate predictions
        df_grouped = df_result.groupby(['Month', 'Medicine', 'Disease']).agg({
            'Predicted Quantity': 'sum'  # Sum quantities for each month, medicine, and disease
        }).reset_index()
        
        # Define table styles
        table_styles = [
            {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('border', '3px solid black')]},
            {'selector': 'th', 'props': [('border', '2px solid green')]},
            {'selector': 'td', 'props': [('border', '2px solid green')]}
        ]
        st.write("Predicted Quantities:")
        for month, group in df_result.groupby('Month'):
            st.markdown(f"### {month}")
            st.table(group.drop(columns='Month').style.set_table_styles(table_styles))
        
        
        # Prepare data for future months
        future_months = np.arange(1, 13)
        predicted_data = pd.DataFrame({'Month': future_months})

        for medicine in Medicines:
            for disease in df[df['Medicine'] == medicine]['Disease'].unique():
                predicted_values = []
                for month in future_months:
                    month_name = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                                  7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November',
                                  12: 'December'}[month]
                    input_data = preprocess_input(Year, month_name, [medicine], Season, feature_columns, df)
                    
                    if input_data is None:
                        return
                    
                    preds = model.predict(input_data)
                    predicted_values.append(int(round(preds[0])))
                
                predicted_data[f'{medicine}_{disease}'] = predicted_values
        
        predicted_data_long = predicted_data.melt(id_vars=['Month'], var_name='Medicine_Disease', value_name='Predicted Quantity')
        
        st.subheader('Predicted Trend for Selected Medicines in Future Months')
        line_chart = alt.Chart(predicted_data_long).mark_line().encode(
            x='Month:Q',
            y='Predicted Quantity:Q',
            color='Medicine_Disease:N',
            tooltip=['Month', 'Medicine_Disease', 'Predicted Quantity']
        ).properties(
            width=800,
            height=400
        ).configure(background='#045F5F').interactive()
        
        st.altair_chart(line_chart)

if __name__ == '__main__':
    show_predict_page()
