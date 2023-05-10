from __future__ import annotations

import json

import requests  # type: ignore
import streamlit as st
from ansi2html import Ansi2HTMLConverter
from dotenv import load_dotenv
from streamlit_chat import message as ChatMessage
import os

load_dotenv()


def main():
    st.title("Find Your Right Talents Within Minutes!")

    # Response container
    responseContainer = st.container()

    # Initialise session state variables
    if "generated" not in st.session_state:
        st.session_state["generated"] = []
    if "past" not in st.session_state:
        st.session_state["past"] = []
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
    if "model_name" not in st.session_state:
        st.session_state["model_name"] = []

    # Using the "with" syntax
    with st.form(key="user_input", clear_on_submit=True):
        question = st.text_input(
            label="Enter what you need to find here",
            placeholder="Find an engineer in Vietnam",
        )
        submit_clicked = st.form_submit_button(
            label="Submit",
            on_click=submitHandler(st.session_state, question),
        )

    # Display messages
    displayMessages(responseContainer, st.session_state)


def displayMessages(container, session_state):
    if session_state["generated"]:
        with container:
            for i in range(len(st.session_state["generated"])):
                ChatMessage(
                    st.session_state["past"][-1], is_user=True, key=str(i) + "_user"
                )
                ChatMessage(
                    st.session_state["generated"][-1], is_user=False, key=str(i)
                )


def submitHandler(session_state, question):
    if not question or len(question) == 0:
        # st.error("Please enter your question")
        return
    # Append user message
    session_state["messages"].append({"role": "user", "content": question})
    session_state["past"].append(question)

    with st.spinner(text="Running agent..."):
        finalResponseText = handleQuestion(question)
        # Receive and display server responses
        session_state["messages"].append(
            {"role": "assistant", "content": finalResponseText}
        )
        session_state["generated"].append(finalResponseText)


def handleQuestion(question: str):
    host = f"http://localhost:{os.environ['BACKEND_PORT']}/ask"
    header = {"Content-Type": "application/json"}
    payload = json.dumps({"question": question})
    response = requests.request("POST", host, headers=header, data=payload)

    answer = response.json()["result"]
    # # The following is for writing without a container
    # if answer:
    #     ansi_convertor = Ansi2HTMLConverter(inline=True)
    #     answer = ansi_convertor.convert(answer).replace("\n", "<br>")
    #     st.write(answer, unsafe_allow_html=True)
    return answer


if __name__ == "__main__":
    main()
