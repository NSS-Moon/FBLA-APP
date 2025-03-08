import streamlit as st
import requests
import json
import time

API_KEY = "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"  # Replace with your OpenRouter API Key
BASE_URL = "https://openrouter.ai/api/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# Variables
decision_count = 0
max_decisions = 10
messages = []

def ask_ai(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            payload = {
                "model": "openai/gpt-4o-latest",  # Use the GPT-4o model
                "messages": messages  # Send the conversation history
            }

            # Send the POST request to OpenRouter API
            response = requests.post(BASE_URL, headers=headers, json=payload, timeout=10)

            # Check if the response is successful
            if response.status_code == 200:
                response_json = response.json()
                return response_json["choices"][0]["message"]["content"]
            else:
                st.error(f"Error: {response.status_code}, {response.text}")
                return "⚠️ Failed to get a response. Please try again later."
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")
            time.sleep(2)  # Wait before retrying
    return "⚠️ Failed to get a response. Please try again later."

def start_story(genre):
    prompt = f"Create a detailed and engaging interactive story in the {genre} genre. The story should start with an immersive opening scene. The AI should continue the story based on whatever action the user provides, without suggesting options."
    return ask_ai([{"role": "system", "content": "You are an interactive storyteller."},
                   {"role": "user", "content": prompt}])

def continue_story(decision):
    global messages
    messages.append({"role": "user", "content": decision})
    return ask_ai(messages)

# Streamlit UI
def main():
    global decision_count, messages

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
                st.error("Please enter a decision! ")
   
    # End story if 10 decisions have been made
    if decision_count >= max_decisions:
        st.write('The story has ended after 10 decisions.')
        if st.button("Reset Game"):
            decision_count = 0
            messages = []
            st.write("Game has been reset. Enter a genre to start again.")

if __name__ == "__main__":
    main()
