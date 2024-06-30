import fitz
import time
from pathlib import Path
import os
import win32com.client as win32 #pywin32 library
from osProcessor import osProcessor
import logging

osProcessing = osProcessor()

class Preprocess:
     
    EMPTY_STRING           = ""
    WORD_EXTENSIONS = ['.doc', '.docx']
    logger                 = logging.getLogger(__name__)
    PDF_FORMAT = 17


    def move_bad_files(self, bad_file_list,bad_files_dir):
        try:
            for bad_file in bad_file_list:
                name = os.path.basename(bad_file)
                print('name',name)
                destination = os.path.join(fr'{bad_files_dir}', name)
                print(f"Moving file: {bad_file}")
                print(f"To destination: {destination}")
                os.rename(bad_file, destination)
                self.logger.info(f"Bad file moved to '{destination}'.")

        except Exception as e:
                self.logger.critical(f'Error due to {e}', exc_info=True)

    def pre_process(self, source_folder, bad_files_dir):
        try:    
            valid_files_list = []
            bad_files_list = []

            status,all_file_list = osProcessing.get_list_all_files_in_dir(source_folder)
            if status:
                for file in all_file_list:
                    status= osProcessing.check_file_validity(file)

                    if status:
                        valid_files_list.append(file)
                    else:
                        bad_files_list.append(file)
                    
                self.move_bad_files(bad_files_list,bad_files_dir)

                return True,valid_files_list, bad_files_list
            
        except Exception as e:    
            self.logger.critical(f'Error due to {e}', exc_info=True)
            return False,self.EMPTY_STRING,self.EMPTY_STRING


        
    def save_as_txt_file(self,raw_text,txt_files_folder,txt_file_name,extension=".txt"):

        try:
            ENCODING_VALUE='utf-8'

            file_path=osProcessing.create_path_name(txt_files_folder,txt_file_name,extension)
        
            with open(file_path, 'w', encoding=ENCODING_VALUE) as file:
                file.write(f"{raw_text}")
                return True
                
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            return False
        
    def getting_text(self,file):
        try:
            text = ""
            for page in file:
                text += page.get_text()
            return True,text

        
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            return False, self.EMPTY_STRING
        
    def name_processing(self,name):

        try:
            if "Naukri" in name:
                phase1 = name.split('_')
                phase2 = phase1[1].split('[')
                return phase2[0]
            
            elif 'profile' in name.lower():
                phase1 = name.split('\\')
                phase2 = phase1[2]

                if '_' in phase2:
                    phase3 = phase2.split('_')
                    return phase3[0]
                else:
                    return phase2
            else:
                return name
            
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)    

    def checkExtension_ConvertToPDF(self, file_path, temp_dir):
        try:
            file_path = os.path.abspath(file_path)  # Convert to absolute path
            status, name = osProcessing.get_file_stem(file_path)
            status, extension = osProcessing.get_file_extension(file_path)

            if status:
                if extension.lower() in self.WORD_EXTENSIONS:
                    success, converted_pdf_path = self.convert_doc_to_pdf(file_path, temp_dir)
                    if not success:
                        return False, None
                    return True, converted_pdf_path
                elif extension.lower() == '.pdf':
                    return True, file_path
                else:
                    return False, None
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            

    def convert_doc_to_pdf(self, word_file, temp_dir):
        status, name = osProcessing.get_file_stem(word_file)

        if status:
            destination_path = os.path.join(temp_dir, name + '.pdf')

            try:
                # Initialize COM
                win32.pythoncom.CoInitialize()

                # Create Word application object
                word_app = win32.Dispatch("Word.Application")

                # Delay to allow Word application to initialize
                time.sleep(1)

                # Open the document
                document = word_app.Documents.Open(word_file)

                # Delay to allow document to be opened
                time.sleep(1)

                # Save as PDF
                document.SaveAs(destination_path, FileFormat=self.PDF_FORMAT)

                # Close document and Quit Word
                document.Close()
                word_app.Quit()

                # Uninitialize COM
                win32.pythoncom.CoUninitialize()

                return True, destination_path
            except Exception as e:
                print(f'Error converting document to PDF: {e}')
                self.logger.critical(f'Error due to {e}', exc_info=True)
                # Uninitialize COM if an error occurs to avoid leaks
                win32.pythoncom.CoUninitialize()
                return False, None
        else:
            return False, None