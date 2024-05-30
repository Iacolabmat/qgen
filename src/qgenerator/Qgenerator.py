import os
import json
import pandas as pd
import traceback
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
from langchain_community.callbacks import get_openai_callback

from src.qgenerator.utils import read_file, get_table_data
from src.qgenerator.logger import logging


from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain


# load environment variables from .env file
load_dotenv()

# Acces the environment variables just like you would with os.environ
key=os.getenv ("OPENAI_API_KEY")

llm=ChatOpenAI(openai_api_key=key,model_name="gpt-3.5-turbo", temperature=0.5)

template="""
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz  of {number} multiple choice questions for {subject} students in {tone} tone. 
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like  RESPONSE_JSON below  and use it as a guide. \
Ensure to make {number} MCQs
### RESPONSE_JSON
{response_json}

"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template=template
    )

quiz_chain=LLMChain(llm=llm, prompt=quiz_generation_prompt, output_key="quiz", verbose=True)

template2="""
You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity analysis. 
if the quiz is not at per with the cognitive and analytical abilities of the students,\
update the quiz questions which needs to be changed and change the tone such that it perfectly fits the student abilities
Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""
quiz_evaluation_prompt=PromptTemplate(input_variables=["subject", "quiz"], template=template2)

review_chain=LLMChain(llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True)

generate_evaluate_chain=SequentialChain(chains=[quiz_chain, review_chain], input_variables=["text", "number", "subject", "tone", "response_json"],
                                        output_variables=["quiz", "review"], verbose=True,)


def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfFileReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception("error reading the PDF file")
        
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    
    else:
        raise Exception(
            "Unsupportef file format. Only .pdf ans text files suppoprted"
            )


def get_table_data(quiz,str):
    try:

        #Convert the quiz fron a str to a dict
        quiz_dict=json.loads(quiz_str)
        quiz_table_data = []

        #iterate over the quiz dictionary & extract the required information
        for key, value in quiz_dict.items():
            mcq = value["mcq"]
            options = " || ".join(
            [
            f"{option}: {option_value}"
            for option, option_value in value["options"].items()
            ]
              )
            correct = value["correct"]
            quiz_table_data.append({"MCQ": mcq, "Choices": options, "Correct": correct})

        return quiz_table_data

    except Exception as e:
        traceback.print_exception(type(e),e,e.__traceback__)
        return False