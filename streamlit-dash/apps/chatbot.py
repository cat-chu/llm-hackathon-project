import streamlit as st
import openai 
import json

def app():
    st.header("\"Hello! \U0001F44B I'm Fiona.\"")
    openai.api_key = "Insert Your API Key"

    with open('data/sample.json') as json_file:
        data = json.load(json_file)

    def format_prompt():
        user_prompt = f"User's journal entry on day {data['date']}: {data['entry']}"
        return user_prompt
        
    messages = [
    {"role": "system", "content": "You are a mental health counselor named Fiona (sign as Fiona) for this user."}
    ]

    def generate_response(question):
        
        messages.append({'role': 'user', 'content': question})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        content = response['choices'][0]['message']['content']
        messages.append({'role': 'assistant', 'content': content})

        return content

    st.markdown("#### \U0001F49B Fiona's advice from your journal entry... \U0001F49B")
    initial_response = generate_response(format_prompt())
    st.markdown("###### " + initial_response)

    def chat():
        count = 1
        st.markdown("###### \U0001F4D3 note: to end this conversation, type END!")
        question = ''

        while question != 'END':
            question = st.text_input("enter your thoughts here:", key=f"user_input{count}")

            while not question:
                continue
            content = generate_response(question)
            st.markdown("###### " + content)
            count += 1
    st.write("\n")
    chat_button = st.button("click here to speak with Fiona!")
    st.header("example prompts...")
    st.write(f"\U00002753 propose a year-long motivational plan with milestones")
    st.write(f"\U00002753 can you give me some examples of tasks i can add to my calendar to improve my mental health?")
    st.write(f"\U00002753 how can i feel less [insert emotion]?")
    st.write("\n")
    if chat_button:
        chat()