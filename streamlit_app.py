import streamlit as st
import requests
import json
import time

# Set up the API key 
API_KEY = "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"  # Replace with your OpenRouter API Key
BASE_URL = "https://openrouter.ai/api/v1"
ENDPOINT = f"{BASE_URL}/chat/completions"

# Variables
decision_count = 0
max_decisions = 10
messages = []

# Function to interact with the AI using OpenRouter API (with Streaming)
def ask_ai_stream(messages, max_retries=3):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Build the request payload
    data = {
        "model": "openai/gpt-4",  # Specify the model to use (e.g., GPT-4)
        "messages": messages,  # The conversation so far (user and assistant messages)
        "stream": True  # Enable streaming
    }

    # Retry mechanism in case of network errors
    for attempt in range(max_retries):
        try:
            # Make a POST request to the OpenRouter API with streaming enabled
            response = requests.post(ENDPOINT, headers=headers, json=data, stream=True, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses

            # Process the streamed response line by line
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    try:
                        response_json = json.loads(decoded_line)
                        if 'choices' in response_json:
                            yield response_json['choices'][0]['delta']['content']
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")
            time.sleep(2)  # Wait before retrying
    yield "⚠️ Failed to get a response from the AI. Please try again later."

# Start Story
def start_story(genre):
    prompt = f"Create a detailed and engaging interactive story in the {genre} genre. The story should start with an immersive opening scene. The AI should continue the story based on whatever action the user provides, without suggesting options."
    return ask_ai_stream([{"role": "system", "content": "You are an interactive storyteller."},
                   {"role": "user", "content": prompt}])

# Continue Story
def continue_story(decision):
    global messages
    messages.append({"role": "user", "content": decision})
    return ask_ai_stream(messages)

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
        story_generator = start_story(genre)

        # Display the story in the container as it is streamed
        story = ''
        for part in story_generator:
            story += part
            story_container.write(story)

    # If the user wants to continue the story
    if decision_count < max_decisions:
        decision = st.text_input("Enter your action/decision to continue the story:")

        if st.button('Continue'):
            if decision.strip():
                decision_count += 1
                next_part_generator = continue_story(decision)

                # Display the continued story in the container as it is streamed
                next_part = ''
                for part in next_part_generator:
                    next_part += part
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
