import streamlit as st
import pandas as pd
import altair as alt
import warnings
warnings.filterwarnings("ignore")

@st.cache_data
def load_data():
    train_data = pd.read_csv("Model/Historical_Data_2021_Jan_2024.csv")
    train_data["Date"] = pd.to_datetime(train_data["Date"])
    train_data['Date'] = train_data['Date'].dt.to_period("M")
    monthly_sales = train_data.groupby("Date").sum().reset_index()
    monthly_sales['Date'] = monthly_sales['Date'].dt.to_timestamp()
    train_data["Year"] = train_data["Date"].dt.year
    train_data["Month"] = train_data["Date"].dt.month
    return train_data

train_data = load_data()


def show_explore_page():
    st.title('Medicine Consumption Analysis')

    # Data filters
    selected_medicines = st.multiselect("Select Medicines", train_data['Medicine'].unique())
    filtered_data = train_data[train_data['Medicine'].isin(selected_medicines)]

    selected_plot_type = st.selectbox("Select Plot Type", ['Bar Chart', 'Line Plot', 'Box Plot', 'Scatter Plot'])

    if selected_plot_type == 'Bar Chart':
        st.subheader('Bar chart of Quantity(Packets) by Medicine')
        bar_chart = alt.Chart(filtered_data).mark_bar().encode(
            x='Medicine',
            y='Quantity(Packets)',
            color='Medicine',
            tooltip=['Medicine', 'Quantity(Packets)']
        ).configure(background='#045F5F').interactive()
        st.altair_chart(bar_chart, use_container_width=True)

    elif selected_plot_type == 'Line Plot':
        st.subheader('Line Plot of Quantity(Packets) over Time')
        line_chart = alt.Chart(filtered_data).mark_line().encode(
            x='Month',
            y='Quantity(Packets)',
            color='Medicine',
            tooltip=['Month', 'Medicine', 'Quantity(Packets)']
        ).configure(background='#045F5F').interactive()
        st.altair_chart(line_chart, use_container_width=True)

    elif selected_plot_type == 'Box Plot':
        st.subheader('Box Plot of Quantity(Packets) by Medicine')
        box_plot = alt.Chart(filtered_data).mark_boxplot().encode(
            x='Medicine',
            y='Quantity(Packets)',
            tooltip=['Medicine', 'Quantity(Packets)']
        ).configure(background='#045F5F').interactive()
        st.altair_chart(box_plot, use_container_width=True)

    elif selected_plot_type == 'Scatter Plot':
        st.subheader('Scatter Plot of Quantity(Packets) vs Season')
        scatter_plot = alt.Chart(filtered_data).mark_circle().encode(
            x='Month',
            y='Quantity(Packets)',
            color='Medicine',
            size='Season',
            tooltip=['Month', 'Medicine', 'Quantity(Packets)', 'Season']
        ).configure(background='#045F5F').interactive()
        st.altair_chart(scatter_plot, use_container_width=True)


def main():
    st.title('Medicine Sales Data Analysis')
    show_explore_page()

if __name__ == '__main__':
    main()
