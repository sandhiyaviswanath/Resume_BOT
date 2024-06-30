import logging.config
from LLM import llm_model
from pdfProcessor import pdfProcessor
from osProcessor import osProcessor
from Embeddings import Embedding
from preprocessor import Preprocess
from deeplake_db import DeeplakeDB
import streamlit as st
from io import StringIO
from dotenv import load_dotenv, find_dotenv
import base64
import openai
import os
import fitz
import logging
import sys
from pathlib import Path

current_folder = str(Path(__file__).resolve().parent)
sys.path.append(current_folder)


logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simpleFormatter': {
            'format': '\n---------------------------------------------------------------------------------------------------------------------\n%(asctime)s - %(name)s(%(funcName)s) - %(levelname)s\n%(message)s'
        }
    },
    'handlers': {
        'fileHandler': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'simpleFormatter',
            'filename': r'.\TS_Logs\TalentSeeker_Logs.log',
            'encoding': 'utf-8'
        }

    },
    'loggers': {
        'root': {
            'level': 'DEBUG',
            'handlers': ['fileHandler']
        },
        'pdfProcessor': {
            'level': 'DEBUG',
            'handlers': ['fileHandler'],
            'qualname': 'pdfProcessor'
        },
        'preprocessor': {
            'level': 'DEBUG',
            'handlers': ['fileHandler'],
            'qualname': 'preprocessor'
        },
        'docProcessor': {
            'level': 'CRITICAL',
            'handlers': ['fileHandler'],
            'qualname': 'docProcessor'
        },
        'Embeddings': {
            'level': 'DEBUG',
            'handlers': ['fileHandler'],
            'qualname': 'Embeddings'
        },
        'osProcessor': {
            'level': 'DEBUG',
            'handlers': ['fileHandler'],
            'qualname': 'osProcessor'
        },
        'LLM': {
            'level': 'DEBUG',
            'handlers': ['fileHandler'],
            'qualname': 'LLM'
        },
        
        'deeplake_db': {
            'level': 'DEBUG',
            'handlers': ['fileHandler'],
            'qualname': 'deeplake_db'

        }
    }
}



llm_obj = llm_model()
pdf_obj = pdfProcessor()
emb_obj = Embedding()
os_obj = osProcessor()
preprocess_obj = Preprocess()
db_obj = DeeplakeDB()


_, config_path = llm_obj.get_config_path()

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

_ = load_dotenv(find_dotenv())  # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

st.set_page_config(layout="wide")


def create_responses(job_description):
    try:
        jd_embeddings = emb_obj.create_embeddings_for_jd(job_description)

        os_obj.create_dir_if_not_exists('badfiles')
        os_obj.create_dir_if_not_exists('temp')

        _, _, list_bad_files = preprocess_obj.pre_process(folder_path, './badfiles')

        resume_text, resume_paths, badfiles = llm_obj.process_resume_folder(folder_path)
        print(f'{len(resume_text)}')

        response_list = emb_obj.create_embeddings_for_resumes(resume_text)
        vectors = [emb.embedding for key, value in response_list if key == 'data' for emb in value if hasattr(emb, 'embedding')]
        db = db_obj.create_deeplake_database(resume_text,vectors,dataset_path)
        results = db_obj.vector_search(db,jd_embeddings)
        print('result',results)
        if results:
            st.header("Ranking the Resumes based on Job Description")
            text_list = results['text']
            score_list = results['score']

        response = llm_obj.generate_profile_summary(score_list,text_list,job_description)
        for i in response:
            st.write(i)
    except Exception as e:
            logger.critical(f'Error due to {e}', exc_info=True)


# Streamlit app
st.title("🚀 Resume Analysis Bot")
st.subheader("🪢 Langchain + 🎁 OpenAI")
 
folder_path = r".\Profiles"
dataset_path = r".\deeplake_dataset"

disabled = False

uploaded_file = st.file_uploader("upload your job description here",type=["pdf"])

if uploaded_file is not None:
    disabled = True
    print('file upload succesfully')
    pdf_bytes = uploaded_file.getvalue()
 
    pdf_document = fitz.open(stream = pdf_bytes)
    job_description = ""
    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)
        job_description += page.get_text()
    create_responses(job_description)

keywords = st.chat_input("Enter keywords to generate Job Description.",disabled= disabled)

 
if keywords is not None:
   
    st.header("Generate Job Description and Analyze Resumes")
    keywords_list = [keyword.strip().lower() for keyword in keywords.split(",")]
    job_description = llm_obj.generate_job_description(keywords_list)
   
    st.markdown(f"### Download Job Description as PDF")
    download_link = f'<a href="data:application/pdf;base64,{base64.b64encode(open(pdf_obj.create_pdf(job_description), "rb").read()).decode()}" download="Job_Description.pdf">Download Job Description</a>'
    st.markdown(download_link, unsafe_allow_html=True)
    create_responses(job_description)

