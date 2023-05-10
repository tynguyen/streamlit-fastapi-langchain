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
        # TODO remove:
        response_chunks = finalResponseText.split("!!!!!!!!")
        session_state["generated"].append(finalResponseText)
        # for chunk in response_chunks:
        #     session_state["generated"].append(chunk)


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

    # Format the  Json answer
    # import pdb

    # pdb.set_trace()
    try:
        json.loads(answer)
        return convertJsonResponseToPlainText(answer)
    except:
        return answer


def convertJsonResponseToPlainText(response):
    response = json.loads(response)
    newLine = "\n"
    try:
        total = response["total"]
        if total == 0:
            responseText = f"Oops! We found {total} candidates that match your search. However, talents are still there. Would you mind rewrite the description with some relaxation?"
            return responseText
        responseText = f"Great! We found totally {total} candidates that match your search. Among these, the top two are: "
        # TODO: hardcode for now
        for record in response["data"]:
            full_name = record["full_name"].title()
            skills = record["skills"]
            experience = record["experience"]
            try:
                experience = experience.title()
            except:
                experience = [x.title() for x in experience]
            mobile_phone = record["mobile_phone"]
            location_country = record["location_country"]
            try:
                location_country = location_country.title()
            except:
                location_country = [x.title() for x in location_country]
            personal_emails = record["personal_emails"]
            linkedin_url = record["linkedin_url"]
            # responseText += "!!!!!!!!"  # magic substring to divide the long message into chunks (for display)
            responseText += (
                newLine
                + "-----------------------------------------------------------------------"
                + newLine
            )
            responseText += f"- {full_name}"
            responseText += newLine + f" Contact: {mobile_phone}"
            responseText += newLine + f" Email: {personal_emails}"
            responseText += newLine + f" LinkedIn: {linkedin_url}"
            responseText += newLine + newLine + f" Skills: {skills}"
            responseText += newLine + newLine + f" Experience: {experience}"
            responseText += newLine + newLine + f" Location: {location_country}"

        return responseText

    except:
        return json.dumps(response)


if __name__ == "__main__":
    main()
