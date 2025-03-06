import streamlit as st
import requests
import time

# Set up the AI21 Labs API key (replace with your actual key)
API_KEY = "c999c2e8-cd38-478f-bc3c-de26d1018610"  # Replace with your API key from AI21 Labs
API_URL = "https://api.ai21.com/studio/v1/j1-jumbo/complete"  # Correct Jurassic-1 Jumbo Model endpoint

# Variables
decision_count = 0
max_decisions = 10
messages = []


# Function to interact with the AI21 Labs API (Jurassic-1)
def ask_ai(messages, max_retries=3):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = " ".join([msg["content"] for msg in messages])  # Combine the messages for prompt

    data = {
        "prompt": prompt,
        "maxTokens": 500,  # You can adjust this value to control response length
        "temperature": 0.8,  # Controls the randomness of the response
        "topP": 1,  # Controls diversity via nucleus sampling
        "stopSequences": ["\n"]  # Optionally, specify stop sequences
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json=data, timeout=10)
            response_json = response.json()
            if "completion" in response_json:
                return response_json["completion"]
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
    
    st.title('FBLA Marvin TGV 2025 - Interactive Story')

    # Genre input to start the story
    genre = st.text_input("Enter a genre for your story:")
    
    # If the user has inputted a genre, start the story
    if genre and decision_count == 0:
        decision_count = 0  # Reset decision count
        messages = [{"role": "system", "content": "You are an interactive storyteller."}]
        story = start_story(genre)
        messages.append({"role": "assistant", "content": story})
        st.write(story)

    # If the user wants to continue the story
    if decision_count < max_decisions:
        decision = st.text_input("Enter your action/decision to continue the story:")

        if st.button('Continue'):
            if decision.strip():
                decision_count += 1
                next_part = continue_story(decision)
                messages.append({"role": "assistant", "content": next_part})
                st.write(next_part)
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
