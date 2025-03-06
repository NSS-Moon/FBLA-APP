import streamlit as st
import requests
import time

# Set up the OpenRouter API key (replace with your actual key)
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Variables
decision_count = 0
max_decisions = 10
messages = []

# Function to interact with the AI
def ask_ai(messages, max_retries=3):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {"model": "openai/gpt-3.5-turbo", "messages": messages, "max_tokens": 500, "temperature": 0.8}

    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json=data, timeout=10)
            response_json = response.json()
            if "choices" in response_json and response_json["choices"]:
                return response_json["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException:
            time.sleep(2)  # Wait before retrying
    return "⚠️ Failed to get a response from the AI. Please try again later."


# Start Story
def start_story(genre):
    prompt = f"Create a detailed and engaging interactive story in the {genre} genre. The story should start with an immersive opening scene. The AI should continue the story based on whatever action the user provides, without suggesting options."
    return ask_ai([{"role": "system", "content": "You are an interactive storyteller."},
                   {"role": "user", "content": prompt}])


# Continue Story
def continue_story(decision):
    global messages
    messages.append({"role": "user", "content": decision})
    return ask_ai(messages)


# Streamlit UI
def main():
    global decision_count, messages

    # Inject custom styles to make the text retro themed and set the background color to purple
    st.markdown(
        """
        <style>
            /* Retro font and background */
            @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

            body {
                background-color: #6A0DAD;  /* Purple background */
                color: white;
                font-family: 'Press Start 2P', cursive;
                font-size: 18px;
            }

            .stTextInput, .stButton, .stTextArea {
                background-color: #4A0072;
                color: #F1E6FA;
                border: 2px solid #F1E6FA;
                font-family: 'Press Start 2P', cursive;
                font-size: 18px;
            }

            .stButton>button {
                background-color: #9B30FF;
                color: #F1E6FA;
                border: 2px solid #F1E6FA;
                font-family: 'Press Start 2P', cursive;
                font-size: 18px;
            }

            .stButton>button:hover {
                background-color: #6A0DAD;
            }

            .stTextArea>textarea {
                background-color: #4A0072;
                color: #F1E6FA;
                border: 2px solid #F1E6FA;
                font-family: 'Press Start 2P', cursive;
                font-size: 18px;
            }

            .stTitle {
                color: #F1E6FA;
            }
        </style>
        """, unsafe_allow_html=True
    )

    st.title('FBLA Marvin TGV 2025 - Interactive Story')

    # Use st.empty() for a scrollable container to dynamically update text
    story_container = st.empty()

    # Genre input to start the story
    genre = st.text_input("Enter a genre for your story:")
   
    # If the user has inputted a genre, start the story
    if genre and decision_count == 0:
        decision_count = 0  # Reset decision count
        messages = [{"role": "system", "content": "You are an interactive storyteller."}]
        story = start_story(genre)
        messages.append({"role": "assistant", "content": story})
        # Display the story in the container
        story_container.write(story)

    # If the user wants to continue the story
    if decision_count < max_decisions:
        decision = st.text_input("Enter your action/decision to continue the story:")

        if st.button('Continue'):
            if decision.strip():
                decision_count += 1
                next_part = continue_story(decision)
                messages.append({"role": "assistant", "content": next_part})
                # Update the story by appending the new part
                story_container.write("\n" + next_part)
            else:
                st.error("Please enter a decision!")
   
    # End story if 10 decisions have been made
    if decision_count >= max_decisions:
        st.write('The story has ended after 10 decisions.')
        if st.button("Reset Game"):
            decision_count = 0
            messages = []
            st.write("Game has been reset. Enter a genre to start again.")

    # Reset game functionality
    if st.button("Reset Game"):
        decision_count = 0
        messages = []
        st.write("Game has been reset. Enter a genre to start again.")

if __name__ == "__main__":
    main()
