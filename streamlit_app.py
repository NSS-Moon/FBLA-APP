import streamlit as st
import requests
import time
import json

# Set up the API key securely (store it in Streamlit's secrets or environment variables)
API_KEY = "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"  # This assumes you've added it to the Streamlit secrets.toml
API_URL = "https://openrouter.ai/v1/gpt4"  # Ensure this URL is correct

# Variables
MAX_DECISIONS = 10
decision_count = 0
messages = []

# Function to interact with the AI
def ask_ai(messages, max_retries=3):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Create the payload (you may need to adjust the format to fit OpenRouter's API)
    data = {
        "messages": messages
    }

    # Retry mechanism in case of network errors
    for attempt in range(max_retries):
        try:
            # Send the POST request to the API
            response = requests.post(API_URL, headers=headers, json=data, timeout=10)
            
            # Log the response status code and content for debugging
            st.write(f"Response Status Code: {response.status_code}")
            st.write(f"Response Content: {response.text}")  # Log the raw response content

            # Check if the response is valid
            response.raise_for_status()  # This will raise an error for HTTP errors (non-2xx status codes)

            # Try to parse the response as JSON
            try:
                response_json = response.json()
                # Ensure the response contains valid output
                if "generated_text" in response_json:
                    return response_json["generated_text"]
                else:
                    return "⚠️ No valid response from AI. Please try again later."
            except json.JSONDecodeError:
                return "⚠️ Response is not valid JSON. Please check the server logs or contact support."
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")
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
    if decision_count < MAX_DECISIONS:
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
    if decision_count >= MAX_DECISIONS:
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
