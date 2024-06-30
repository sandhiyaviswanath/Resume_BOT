from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pdfProcessor import pdfProcessor
from preprocessor import Preprocess
import datetime
import shutil
import os
import openai
import logging
from osProcessor import osProcessor

os_pro= osProcessor()

pdf_obj = pdfProcessor()
preProcess_obj = Preprocess() 

class llm_model():
    logger    = logging.getLogger(__name__)
    EMPTY_STR = ''


    def get_llm_model(self):
        try:
            # Define the date after which the model should be set to "gpt-3.5-turbo"
            current_date = datetime.datetime.now().date()
            target_date = datetime.date(2024, 6, 12)
            llm_model = "gpt-3.5-turbo" if current_date > target_date else "gpt-3.5-turbo-0301"
            return llm_model
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
           

    def initiate_Langchain(self):
    # Initialize LangChain
        try:
            llm_model = self.get_llm_model()
            chat = ChatOpenAI(temperature=0.0, model=llm_model)
            return chat
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)

    def generate_job_description(self,keywords):
        try:
            prompt = f"""Generate an appropriate job description for {keywords} with description,
            requirements, responsibilities, and needed technical skills which is suitable for the given {keywords}.
            """
            chat = self.initiate_Langchain()
            prompt_template = ChatPromptTemplate.from_template(prompt)
            customer_messages = prompt_template.format_messages(text=prompt_template)
            customer_response = chat.invoke(customer_messages).content
            return customer_response
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
    
    def process_resume_folder(self, folder_path):
            
        try:    
            resume_texts = []
            resume_paths = []
            bad_files = []  # To store filenames of bad files
            encountered_emails = set()
            encountered_phones = set()
            unsupported_files = []  # To store unsupported files
            # Temporary folder to store converted PDFs
            temp_dir = os.path.join(os.getcwd(), 'temp')

            for filename in os.listdir(folder_path):
                if filename.endswith(".pdf"):
                    pdf_path = os.path.join(folder_path, filename)
                else:
                    pdf_path = os.path.join(folder_path, filename)
                    success, converted_pdf_path = preProcess_obj.checkExtension_ConvertToPDF(pdf_path, temp_dir)
                    if not success:
                        unsupported_files.append(pdf_path)
                        continue
                    pdf_path = converted_pdf_path

                with open(pdf_path, 'rb') as file:
                    text = pdf_obj.extract_text_from_pdf(file)

                # Extract name, email, and phone number
                email, phone = pdf_obj.extract_emailPhone_from_PDF(text)

                if (email and email in encountered_emails) or (phone and phone in encountered_phones):
                    bad_files.append(pdf_path)
                    shutil.move(pdf_path, "./badfiles")
                else:
                    # Add email and phone number to encountered sets
                    if email:
                        encountered_emails.add(email)
                    if phone:
                        encountered_phones.add(phone)

                    resume_texts.append(text)
                    resume_paths.append(pdf_path)

            return resume_texts, resume_paths, bad_files

        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)

        

    def get_config_path(self):
        try:
            _ , parent_dir = os_pro.get_code_dir()
            _, grandParent_dir = os_pro.get_parent_dir(parent_dir)
            _ , qual_config_file_name = os_pro.join_paths('logging.conf', grandParent_dir, 'TS_Config')

            return True, qual_config_file_name

        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)

            return False, self.EMPTY_STR

    
    def generate_profile_summary(self,text_list,score_list,job_description,max_tokens_per_request = 4000):

        try:    
            prompt = f"""hey, Hey Act Like a skilled ATS tracking system
            with a deep understanding of tech field,software engineering,data science ,data analyst
            and big data engineer. Your task is to get the profile summary of the given resumes.
            give the results based on the similarity score.
            check the context of job desription and resume is getting matched, if not
            then dont make up the answer or dont try to give the ranking of resumes for irrelevant ones.
            just say the given job description and resume does not match, so I am not able to tell who is the best fit for this job description.
            give the profile summary correctly.maintain the ranking based on the similarity score only. I want the sorting based on similarity score.
            And then give the results.The score list is the scores of each resume, the first score is
            the score of first resume in text list so you have to take the score like that and give the
            results correctly, just take the resume from text list and take the score then give 
            the result. Dont rank it with job description, while giving the result maintain the
            order which is in text list.
            resume:{text_list}
            description:{job_description}
            similarity score:{score_list}
            {{"name":"",
            "similarity_score":"%",
            "Profile Summary":""}}
            """

            response = openai.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0,
                    max_tokens=max_tokens_per_request, 
                    seed= 123       
                )
                # Extract and parse the ranked list from the GPT-3 response
            response_to_show_in_UI = response.choices[0].message.content.split("\n")

            return response_to_show_in_UI
        
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
    
    