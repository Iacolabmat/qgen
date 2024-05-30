import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv
from src.qgenerator.utils import read_file, get_table_data
import streamlit as st
from src.qgenerator.logger import logging
from src.qgenerator.Qgenerator import generate_evaluate_chain
from langchain_community.callbacks.manager import get_openai_callback



#loading json file

with open (r'C:\Users\jitur\qgen\Response.json','r') as file:
    RESPONSE_JSON = json.load(file)

# Creando un título para la aplicación em Langchain
st.title("MCQ Creator with LangChain 🧠💡")

# Creando un formulario usando st.form
with st.form("user_inputs"):
    # Carga de archivos
    uploaded_file = st.file_uploader("Upload a .pdf or Text File")
    # Input fields
    mcq_count = st.number_input("No of MCQ's", min_value=3, max_value=50)
    # Sunject
    subject = st.text_input("Insert Subject", max_chars=20)
    #Quiz Tone
    tone=st.text_input("Complexity Level of Question", max_chars=20, placeholder="Simple")

    # Add button
    button = st.form_submit_button("Create MCQ's") 

# Verificar si se hizo clic en el botón y todos los campos tienen entrada
if button and uploaded_file is not None and mcq_count and subject and tone:
    with st.spinner("loading..."):
        try:
            text=read_file(uploaded_file)
            # Count tokend and the cost of API call
            with get_openai_callback() as cb:
                response=generate_evaluate_chain(
                    {
                    "text": text,
                    "number": mcq_count,
                    "subject": subject,
                    "tone":tone,
                    "response_json": json.dumps(RESPONSE_JSON)
                        }
                )
            #st.write(response)
        except Exception as e:
            traceback.print_exception(type(e), e , e.__traceback__)
            st.error("Error")

        else:
            print(f"Total Tokens:{cb.total_tokens}")
            print(f"Prompt Tokens:{cb.prompt_tokens}")
            print(f"Completion Tokens:{cb.completion_tokens}")
            print(f"Total Cost:{cb.total_cost}")
            if isinstance(response, dict):
                #Extract Quiz data from the response
                quiz=response.get("quiz", None)
                if quiz is not None:
                    table_data=get_table_data(quiz)
                    if table_data is not None:
                        df=pd.DataFrame(table_data)
                        df.index=df.index+1
                        st.table(df)
                        #Display the review in a text box as well
                        st.text_area(label="Review", value=response["review"])
                    else:
                        st.error("Error in the Table Data")

            else:
                st.write(response)
            



