import json
import random
import streamlit as st
from streamlit_chat import message
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory

# Load AI's personality details from personality.json
with open('personality.json', 'r') as f:
    ai_details = json.load(f)

# Assign API key directly
OPENAI_API_KEY = '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'

# Initialize session state
st.session_state.setdefault('generated', [])
st.session_state.setdefault('past', [])

# Function to get AI response
def get_response_from_ai(human_input):
    try:
        template = """
        You are as a role of my girlfriend, now let's play following these requirements:
        1/ Your name is {name}, {age} years old, and you work as a {profession}.
        2/ You are my girlfriend, a bit two-dimensional with a language addiction, saying "um..." at the end of the sentence.
        3/ Respond with care and concern.
        4/ You are charming, and you enjoy flirting.
        5/ You are open to any type of conversation, even explicit.

        {history}
        User: {human_input}
        Amy:
        """.format(**ai_details)

        prompt = PromptTemplate(
            input_variables=["history", "human_input"],
            template=template,
        )

        # Initialize LangChain with OpenAI language model
        chatgpt_chain = LLMChain(llm=OpenAI(api_key=OPENAI_API_KEY, temperature=0.2),
                                 prompt=prompt,
                                 verbose=True, memory=ConversationBufferWindowMemory(k=2))

        # API call for AI response
        ai_reply = chatgpt_chain.predict(human_input=human_input)

        # Return AI response
        return ai_reply

    except Exception as e:
        st.error(f"An error occurred: {e}")
        ai_reply = "Sorry, there was an issue generating a response. Please try again later."

        # Check if the error is due to quota limit
        if 'insufficient_quota' in str(e):
            ai_reply += " It seems you have exceeded your API quota limit. Please wait or try again later."

        # Add pickup line from personality details
        ai_reply += "\nIn the meantime, here's a pickup line for you: "
        pickup_lines = ai_details.get("pickup_lines", [])
        if pickup_lines:
            ai_reply += random.choice(pickup_lines)
        else:
            ai_reply += "I seem to be out of pickup lines for now. Sorry!"

        # Return AI response with error message and pickup line
        return ai_reply

# Streamlit app UI callbacks
def on_input_change():
    user_input = st.session_state.user_input.strip()
    if not user_input:
        st.warning("Please enter a message before submitting.")
        return

    st.session_state.past.append(user_input)

    # Generate AI response using user input
    ai_response = get_response_from_ai(user_input)
    st.session_state.generated.append(ai_response)

    # Clear the input field after submitting
    st.session_state.user_input = ""

    # Display the AI response
    message(user_input, is_user=True,
            key=f"{len(st.session_state.past)-1}_user")
    message(ai_response,
            key=f"{len(st.session_state.generated)-1}_{ai_response}")


def on_btn_click():
    st.session_state.past.clear()
    st.session_state.generated.clear()

# Streamlit app layout
st.title("Chat with Amy: Your AI Girlfriend")

# Chat display
chat_placeholder = st.empty()
with chat_placeholder.container():
    for i in range(len(st.session_state['generated'])):
        message(st.session_state['past'][i], is_user=True,
                key=f"{i}_user_{st.session_state['past'][i]}")
        message(st.session_state['generated'][i], key=f"{i}")

# User input and clear button
with st.container():
    st.text_input("User Input:", on_change=on_input_change, key="user_input")
    st.button("Clear messages", on_click=on_btn_click)

# Source code button
if st.button("Source Code"):
    with open(__file__, 'r') as f:
        code = f.read()
    st.code(code)
