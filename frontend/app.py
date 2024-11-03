import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, date

# Define the dictionary with dates as keys and text as values
file_path = 'data_diaries.csv'
df = pd.read_csv(file_path)

# Function to recreate the dictionary from the DataFrame
def recreate_data_dict():
    return {
        datetime.strptime(row['date'], '%Y-%m-%d').date(): (row['description'], row['description_vector'])
        for _, row in df.iterrows()
    }

# Initialize data_dict
data_dict = recreate_data_dict()

# Function to add a new entry to the DataFrame and save it to the CSV
def add_entry_to_df(date, description):
    global df
    new_row = {'date': date.strftime('%Y-%m-%d'), 'description': description, 'description_vector': ''}
    df = df.append(new_row, ignore_index=True)
    df.to_csv(file_path, index=False)  # Save the updated DataFrame to the CSV
    return recreate_data_dict()  # Recreate the dictionary from the updated DataFrame

# Main function
def main_page():
    global data_dict  # Declare global at the start of the function
    st.title("Main Page")
    st.write("Welcome to the main page of my Streamlit app!")

    # Date selection
    selected_date = st.date_input("Pick a date")

    # Display event information or option to create a new entry
    if selected_date in data_dict:
        display_journal(selected_date, data_dict[selected_date][0])
    else:
        st.write("No events scheduled for this date.")
        if st.button("Write a journal entry"):
            new_entry = st.text_area("Enter your journal entry for this date:")
            if st.button("Save Entry"):
                # Update DataFrame and CSV, then recreate data_dict
                data_dict = add_entry_to_df(selected_date, new_entry)
                
                st.success("Journal entry saved!")
                
                # Rerun to display the updated entry
                st.experimental_rerun()

# Function to display the journal entry in a styled format
def display_journal(selected_date, event_text):
    st.markdown(f"""
        <style>
        .journal-container {{
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            font-family: Arial, sans-serif;
        }}
        .journal-title {{
            font-size: 24px;
            font-weight: bold;
            color: #333333;
        }}
        .journal-content {{
            font-size: 18px;
            color: #555555;
            margin-top: 10px;
            line-height: 1.6;
        }}
        </style>
        <div class="journal-container">
            <div class="journal-title">Journal Entry for {selected_date.strftime('%B %d, %Y')}</div>
            <div class="journal-content">{event_text}</div>
        </div>
    """, unsafe_allow_html=True)


def second_page():
    st.title("Second Page")
    st.write("This is the second page of my app!")

    # Sample data
    data = pd.DataFrame({
        'Category': ['A', 'B', 'C', 'D', 'E'],
        'Values': [10, 20, 15, 30, 50]
    })

    # Bar chart with Plotly
    fig = px.bar(data, x='Category', y='Values')
    st.plotly_chart(fig)

def third_page():
    st.markdown("""
    <style>
    /* Background animation */
    [data-testid="stAppViewContainer"] {
        animation: backgroundChange 1s;
    }

    @keyframes backgroundChange {
        0% { background-color: #f0f2f6; }
        100% { background-color: #000000; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("Third Page")
    st.write("This is the third page of my app!")

    data = pd.DataFrame({
        'Category': ['Category A', 'Category B', 'Category C', 'Category D'],
        'Values': [15, 30, 45, 10]
    })

    # Create the pie chart
    fig = px.pie(data, names='Category', values='Values', title="Sample Pie Chart")

    # Display the pie chart in Streamlit
    st.plotly_chart(fig)



# Sidebar navigation using buttons
st.sidebar.title("Navigation")

# Check which button is clicked and display the respective page

if st.sidebar.button("Main Page"):
    st.session_state.page = "Main"
if st.sidebar.button("Second Page"):
    st.session_state.page = "Second"
if st.sidebar.button("Third Page"):
    st.session_state.page = "Third"

# Initialize page in session state if it doesn't exist
if "page" not in st.session_state:
    st.session_state.page = "Main"

# Display the selected page based on session state
if st.session_state.page == "Main":
    main_page()
elif st.session_state.page == "Second":
    second_page()
elif st.session_state.page == "Third":
    third_page()
