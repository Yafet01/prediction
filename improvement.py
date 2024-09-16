import streamlit as st
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

@st.cache_resource
def load_model():
    with open('model_saved', 'rb') as f:
        model = pickle.load(f)
    return model
train_data = pd.read_csv("new medicine.csv")

data = load_model()

def preprocess_input(Year, Month, medicines, Season):
    input_data = []
    
    

        
    Medicines = ['Aspirin', 'Ibuprofen', 'Artemisinin', 'Paracetamol', 'Chloroquine', 'Dexamethasone', 'Erythromycin', 'Naproxen', 'Omeprazole', 'Ranitidine', 'Cetirizine']
    disease=["pain", "malaria", "fever", "Arthritis", "Pneumonia", "Diabetes", "Asthma", "Gastritis", "Allergy"]
    df = pd.DataFrame(data)
    conditions={
        'pain':['Aspirin','Ibuprofen'],
        'malaria':[ 'Artemisinin'] ,
        'fever':[ 'Paracetamol','Chloroquine'] ,
        'Arthritis': ['Dexamethasone'] ,
        'Pneumonia':['Erythromycin'] ,
        'Diabetes': ['Naproxen'] ,
        'Asthma': ['Omeprazole'] ,
        'Gastritis': [ 'Ranitidine'] ,
        'Allergy': ['Cetirizine']  
            }
    
    for index, row in df.iterrows():
        for condition, medicines in conditions.items():
            df.at[index, condition] = 1 if row['Medicine'] in medicines else 0

        if Season == 'Wet':
            dry = 0
            wet = 1
        else:
            dry = 1
            wet = 0
        
        input_data.append([Year, Month, fever, malaria, pain, dry, wet, artemisinin, aspirin, ibuprofen, paracetamol])

    return np.array(input_data)

def show_predict_page():
    st.title('Prediction')
    st.write('Please fill in the following details to predict the quantity of medicine needed.')
    Year = st.number_input('Year', min_value=2024)
    Month = st.number_input('Month', min_value=1, max_value=12)
    Season = st.radio('Season', ('Wet', 'Dry'))
    medicines = st.multiselect("Select Medicines", train_data['Medicine'].unique())

    if st.button("Submit"):
        table_data = []
        for medicine in medicines:
            if medicine == 'Paracetamol':
                disease = 'Fever'
            elif medicine == "Artemisinin":
                disease = 'Malaria'
            elif medicine == "Ibuprofen" or medicine=="Aspirin":
                disease = 'Pain'
            
            input_data = preprocess_input(Year, Month, [medicine], Season)
            predictions = data.predict(input_data)
            table_data.append({"Month": Month, "Medicine": medicine, "Disease": disease, "Predicted Quantity": round(predictions[0], 0)})
        
        df = pd.DataFrame(table_data)

        table_styles = [
            {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('border', '3px solid black')]},
            {'selector': 'th', 'props': [('border', '2px solid green')]},
            {'selector': 'td', 'props': [('border', '2px solid green')]}
        ]
        st.write("Predicted Quantities:")
        st.table(df.style.set_table_styles(table_styles))

        plt.figure(figsize=(10, 6))
        for medicine in Medicines:
            future_months = np.arange(1, 13)
            predicted_values = []
            for month in future_months:
                input_data = preprocess_input(Year, month, [medicine], Season)
                preds = data.predict(input_data)
                predicted_values.append(preds[0])
            
            plt.plot(future_months, predicted_values, label=f'{medicine}')

        plt.xlabel('Month')
        plt.ylabel('Predicted Quantity of Medicine')
        plt.title('Predicted Trend for Selected Medicines in Future Months')
        plt.legend()
        st.pyplot()

if __name__ == '__main__':
    show_predict_page()
