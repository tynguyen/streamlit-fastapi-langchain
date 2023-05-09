from __future__ import annotations

import json

import requests  # type: ignore
import streamlit as st
from ansi2html import Ansi2HTMLConverter
from dotenv import load_dotenv
import os

load_dotenv()
question = st.text_input(
    "Type your math question:", placeholder="What 19 to the power 0.43?"
)

submit = st.button("Submit")


def main():
    if submit:
        if not question:
            st.error("Please enter your question")
            return

        with st.spinner(text="Running agent..."):
            host = f"http://localhost:{os.environ['BACKEND_PORT']}/ask"
            header = {"Content-Type": "application/json"}
            payload = json.dumps({"question": question})
            response = requests.request("POST", host, headers=header, data=payload)
            import pdb

            pdb.set_trace()
            answer = response.json()["result"]
            if answer:
                ansi_convertor = Ansi2HTMLConverter(inline=True)
                answer = ansi_convertor.convert(answer).replace("\n", "<br>")
                st.write(answer, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
