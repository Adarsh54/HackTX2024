import random
from datetime import datetime, timedelta

import openai
import pandas as pd
import streamlit as st

openai.api_key = ""

# Define the dictionary with dates as keys and text as values
file_path = 'data_diaries.csv'
df = pd.read_csv(file_path)

# Function to recreate the dictionary from the DataFrame
def recreate_data_dict():
    return {
        datetime.strptime(row['date'], '%Y-%m-%d').date(): (row['description'], row['description_vector'])
        for _, row in df.iterrows()
    }

# # Initialize data_dict
data_dict = recreate_data_dict()


# Function to add a new entry to the DataFrame and save it to the CSV
def add_entry_to_df(date, description):
    global df
    new_row = {'date': date.strftime('%Y-%m-%d'), 'description': description[0], 'description_vector': description[1]}
    df = df.append(new_row, ignore_index=True)
    df.to_csv(file_path, index=False)  # Save the updated DataFrame to the CSV
    return recreate_data_dict()  # Recreate the dictionary from the updated DataFrame

def app_header():
    st.markdown("""
        <style>
        .app-title {
            font-size: 36px;
            font-weight: bold;
            color: #FFFFFF; /* Dark green */
            text-align: center;
            margin-top: -50px;
        }
        .app-subtitle {
            font-size: 18px;
            color: #555555;
            text-align: center;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="app-title">PUT TITLE HERE GUYS 📔</div>', unsafe_allow_html=True)


# Main function
def main_page():
    app_header()
    st.markdown('<div class="app-subtitle">A personal space to reflect, record, and grow</div>', unsafe_allow_html=True)
    page_bg_img = '''
    <style>
    .journal-container {
        background-color: rgba(255, 255, 255, 0.8); /* White with transparency */
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
    }
    .journal-title {
        font-size: 24px;
        font-weight: bold;
        color: #333333;
    }
    .journal-content {
        font-size: 18px;
        color: #555555;
        margin-top: 10px;
        line-height: 1.6;
    }
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

    quotes = [
        "“Journaling is like whispering to one’s self and listening at the same time.” - Mina Murray",
        "“The best way to capture moments is to pay attention. This is how we cultivate mindfulness.” - Jon Kabat-Zinn",
        "“Write what should not be forgotten.” - Isabel Allende",
        "“Fill your paper with the breathings of your heart.” - William Wordsworth"
    ]

    quote = random.choice(quotes)
    st.markdown(f"### 🌟 {quote}")

    # Date selection with visual improvements
    st.write("---")  # Divider line

    global data_dict  # Declare global at the start of the function
    st.title("My Journal")
    st.subheader("📅 Select a Date to View or Add Entries")

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
            border: 2px solid #000000;
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
            <div class="journal-title">🗓️ Journal Entry for {selected_date.strftime('%B %d, %Y')}</div>
            <div class="journal-content">{event_text}</div>
        </div>
    """, unsafe_allow_html=True)

# Function to search for a keyword in journal entries
def search_keyword(keyword):
    results = []
    keyword = keyword.lower()  # Make the search case-insensitive

    for date, description in data_dict.items():
        # Check if the keyword appears in the description
        if keyword in description[0].lower():
            # If relevant, add it to the results
            results.append((date, description))

    return results



def search_emotion(keyword):
    results = []
    for date, description in data_dict.items():
        # Simplified prompt
        prompt = (
            f"Is the following journal entry relevant to the keyword '{keyword}'? "
            f"Please answer 'yes' if it is relevant or 'no' if it is not.\n\nEntry: {description[0]}"
        )

        try:
            # Call ChatCompletion endpoint
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant that determines if journal entries are relevant to a given keyword."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )

            # Extract and interpret the response
            answer = response['choices'][0]['message']['content'].strip().lower()
            if answer == "yes":
                results.append((date, description))

        except Exception as e:
            print("Error:", e)
    
    return results

def second_page():
    # Define the background color using CSS
    page_bg_color = '''
    <style>
    .stApp {
        background-color: #ADD8E6; /* Replace with your preferred color */
    }
    </style>
    '''

    # Inject the CSS into the app
    st.markdown(page_bg_color, unsafe_allow_html=True)

    app_header()

    st.title("Words 📖")
    st.subheader("Search for keywords in your journal entries")

    st.title("Search Journal")
    
    search_term_one = st.text_input("Search your journal", placeholder="Show me an entry with this word in it")
    if search_term_one:
            # Perform search and display results
            results = search_keyword(search_term_one)
            
            if results:
                st.write(f"Found {len(results)} result(s):")
                for date, description in results:
                    display_journal(date, description[0])
            else:
                st.write("No entries found for that keyword.")



def third_page():
    # Define the background color using CSS
    page_bg_color = '''
    <style>
    .stApp {
        background-color: #FFC0CB; /* Replace with your preferred color */
    }
    </style>
    '''

    # Inject the CSS into the app
    st.markdown(page_bg_color, unsafe_allow_html=True)

    app_header()

    st.title("Feelings 💭")
    st.subheader("Search for emotions you felt in your journal entries")

    st.title("Search Journal")
    # Search bar with placeholder text
    search_term = st.text_input("Search your journal", placeholder="Show me an entry where I felt...")

    if search_term:
        # Perform search and display results
        results = search_emotion(search_term)
        
        if results:
            st.write(f"Found {len(results)} result(s):")
            for date, description in results:
                display_journal(date, description[0])
        else:
            st.write("No entries found for that keyword.")

# Function to get journal entries within a date range
def get_entries_in_date_range(start_date, end_date):
    return [
        (date, entry) for date, entry in data_dict.items()
        if start_date <= date <= end_date
    ]

# Function to generate advice based on recent journal entries
def generate_advice(entries):
    # Prepare a summary of recent entries for context
    context = "Here are some recent journal entries:\n"
    for date, entry in entries:
        context += f"- {date.strftime('%B %d, %Y')}: {entry[0]}\n"
    print(context)

    # Create a prompt for ChatGPT with recent entries as context
    prompt = (
        f"{context}\n\nBased on the above journal entries, please provide me with some advice."
    )

    # Call the OpenAI API for advice
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an empathetic assistant that provides thoughtful advice based on journal entries."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    # Extract and return the advice text
    return response['choices'][0]['message']['content']

# Fourth page function (styled as a chatbot)
def fourth_page():
    page_bg_color = '''
    <style>
    .stApp {
        background-color: #3CB371; /* Replace with your preferred color */
    }
    </style>
    '''

    # Inject the CSS into the app
    st.markdown(page_bg_color, unsafe_allow_html=True)

    app_header()

    st.title("Chat with Your Journal 🤖")
    st.subheader("Ask for advice or just chat about your journal entries")

    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for chat in st.session_state.chat_history:
        st.markdown(f"**{chat['role']}:** {chat['content']}")

    # User input
    user_input = st.text_input("You:")

    if st.button("Send") and user_input:
        # Add user input to chat history
        st.session_state.chat_history.append({"role": "You", "content": user_input})

        # Generate response using OpenAI API using journal entries as context
        recent_entries = get_entries_in_date_range(datetime.now().date() - timedelta(days=30), datetime.now().date())
        context = "Here are some recent journal entries:\n"
        for date, entry in recent_entries:
            context += f"- {date.strftime('%B %d, %Y')}: {entry[0]}\n"

        prompt = (
            f"{context}\n\n{user_input}"
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful and empathetic assistant that uses the user's journal entries as context."},
                *[{"role": "user", "content": chat['content']} for chat in st.session_state.chat_history if chat['role'] == "You"],
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        # Extract and add response to chat history
        bot_response = response['choices'][0]['message']['content']
        st.session_state.chat_history.append({"role": "Bot", "content": bot_response})

        # Display the updated chat
        st.experimental_rerun()




# Sidebar navigation using buttons
st.sidebar.title("PUT APP NAME HERE")

# Check which button is clicked and display the respective page

if st.sidebar.button("My Journal"):
    st.session_state.page = "Main"
if st.sidebar.button("Words"):
    st.session_state.page = "Second"
if st.sidebar.button("Feelings"):
    st.session_state.page = "Third"
if st.sidebar.button("Advice"):
    st.session_state.page = "Fourth"

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
elif st.session_state.page == "Fourth":
    fourth_page()
