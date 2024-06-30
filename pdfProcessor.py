import fitz #PyMuPdf Library
import os
import openpyxl
import osProcessor
from tabulate import tabulate
from fpdf import FPDF
import tempfile
import re
import logging


op=osProcessor.osProcessor()

class pdfProcessor:

    IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'pam', 'pbm', 'pgm', 'pnm', 'ppm', 'ps', 'psd', 'png']
    DEBUG=True
    EXCEL_EXTENSION="xlsx"
    TEXT_EXTENSION="txt"
    EMPTY_LIST = []
    logger                 = logging.getLogger(__name__)

    
    def OpenPDFFile(self,file_path):
        try:
            file=fitz.open(file_path)
            # print('file...............',file)
            return True,file
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            return False,file_path
        
    def extract_text_from_pdf(self,pdf_path):
        text = ""
        try:
            with fitz.open(pdf_path) as document:
                for page_num in range(document.page_count):
                    page = document.load_page(page_num)
                    text += page.get_text()
            return text
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
    

    def extract_images(self,pdf_file_path,destination_folder,extension="jpeg"):
        try:
            _, input_file = self.OpenPDFFile(pdf_file_path)
            for page in input_file:
                #.get_images() returns the dict of values for example :
                #{'xref': 1234, 'width': 800, 'height': 600, 'bpc': 8, 'colorspace': 'DeviceRGB', ...}
                '''
                'xref':         A reference identifier for the image within the PDF document.
                'width':        The width of the image in pixels.
                'height':       The height of the image in pixels.
                'bpc':          The number of bits per component for color.
                'colorspace':   The color space of the image (e.g., 'DeviceRGB' for RGB images).
                '''   
                for img in page.get_images(): 
                
                    xref = img[0]
                    #.extract_image(xref) is a dictionary containing the binary image data as img[“image”]. 
                    pix = input_file.extract_image(xref)['image']
                    pix_obj = fitz.Pixmap(pix)#fitz.Pixmap is the constructor for creating a Pixmap object.

            _ ,save_msg =  self.naming_images(pdf_file_path,pix_obj,destination_folder,extension)
            return True,save_msg
        
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            return False, f"{str(e)}"


    def naming_images(self,pdf_file_path,pix_obj,destination_folder,extension):
        try:
                
            file_name = os.path.basename(pdf_file_path)
            name = os.path.splitext(file_name)[0]
            counter = ''
            while os.path.exists(fr'{destination_folder}\_{name}{counter}.{extension}'):
                if counter == '':
                    counter = 1
                else:
                    counter +=1

            _,save_msg=self.saving_image(pix_obj,name,counter,extension,destination_folder)

            return True,save_msg

        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)

            return False, f"{str(e)}"


    def saving_image(self,pix_obj,name,counter,extension,destination_folder):
        try:

            if extension.lower() in self.IMAGE_EXTENSIONS:
                pix_obj.save(fr'{destination_folder}\_{name}{counter}.{extension}')
                return True, fr" saved at {destination_folder}\_{name}{counter}.{extension}"
            
            else:
                return False, "Invalid file extension. Please provide a valid extension."
        
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            return False, f"{str(e)}"


    def underline_string(self,search_string,pdf_file_path,output_file_path):
         try:
            _, input_file = self.OpenPDFFile(pdf_file_path)
            
            for page in input_file:
                for keyword in search_string:
                    text_instances = page.search_for(keyword)

                    for inst in text_instances:
                        underline = page.add_underline_annot(inst)
                        underline.update()

            input_file.save(output_file_path)
            input_file.close()

            return True

         except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            return False

    
    def create_new_text_pdf(self,text,new_pdf_path,x_co=50,y_co=50):
        try:
            document = fitz.open()
            page = document.new_page()
            page.insert_text(fitz.Point(x_co, y_co), text)
            document.save(new_pdf_path)
            return True
        except  Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            return False


    def create_new_image_pdf(self,image_path,new_pdf_path,x_TL=10,y_TL=10,x_BR=100,y_BR=100):
        #( x0, y0, x1, y1 ) A rectangle is called valid if x0 <= x1 and y0 <= y1
        try:
            document = fitz.open()
            page = document.new_page()
            rect=fitz.Rect(x_TL,y_TL,x_BR,y_BR) 
            page.insert_image(rect, filename = image_path)
            document.save(new_pdf_path)
            return True
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            return False

    def create_pdf(self,text):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, text)
        
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            temp_file_name = temp_file.name
            pdf.output(temp_file_name)
            return temp_file_name
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            print('not able to create pdf')

    def extract_emailPhone_from_PDF(self,text):
        try:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email = re.search(email_pattern, text)

            phone_pattern = r'\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\b'
            phone = re.search(phone_pattern, text)

            if email:
                email = email.group(0)
            if phone:
                phone = phone.group(0)

            return email, phone  # Return email and phone number
        
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
    
            return self.EMPTY_LIST, self.EMPTY_LIST
        
    def extract_table_of_contents(self,pdf_file_path):
        toc_entries = []
        try:
            _, input_file = self.OpenPDFFile(pdf_file_path)
            toc = input_file.get_toc() #list of lists. Each entry has the form [lvl, title, page, dest].
            for entry in toc:
                '''Each entry typically contains information about a section or chapter in the PDF, 
                such as its level (indentation), title, and the page number where it can be found.'''
                level, title, page = entry
                toc_entries.append((level, title, page))
            return toc_entries
        
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)

            return toc_entries
        
    def extract_table(self,pdf_file_path):
        table_list=[]
        try:
            _,doc = self.OpenPDFFile(pdf_file_path)
            for page in doc:
                tabs = page.find_tables() # locate and extract any tables on page
                if tabs.tables:  # at least one table found?
                    for tab in tabs:
                        table_list.append(tab.extract()) 

            return True, table_list
        
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            
            return False, table_list

    def append_table_data_in_file(self, pdf_file_path, output_file_path, file_format, file_name="Table_excel", sheet_name="Tables"):
        try:
            _, table_list = self.extract_table(pdf_file_path)

            if file_format == "excel":

                workbook = openpyxl.Workbook()
                sheet = workbook.active
                sheet.title = sheet_name

                for table in table_list:
                    for row in table:
                        sheet.append(row)
                    sheet.append([])

                file_path=op.create_path_name(output_file_path,file_name,self.EXCEL_EXTENSION)
                workbook.save(file_path)

            elif file_format == "text":

                file_path=op.create_path_name(output_file_path,file_name,self.TEXT_EXTENSION)
                with open(file_path, 'w') as output_file:
                    for table in table_list:
                        for row in table:
                            output_file.write(str(row))
                        output_file.write('\n')
            
            elif file_format == "tabulate_text":

                file_path=op.create_path_name(output_file_path,file_name,self.TEXT_EXTENSION)
                with open(file_path, 'w') as output_file:
                    for table in table_list:
                        table_str = tabulate(table, tablefmt="grid")
                        output_file.write(table_str + "\n\n")

            return True,f"Data appended to {file_path}"
        
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)

            return False, f"An error occurred: {str(e)}"
        
    def extract_font_colour(self, pdf_file_path):
        text_color_data = []
        try:
    
            _, pdf_document = self.OpenPDFFile(pdf_file_path)

            for page_number in range(len(pdf_document)):

                page = pdf_document[page_number]

                # Get the text content of the page, including font color
                blocks = page.get_text("dict", flags=11)["blocks"]
                for b in blocks:  # iterate through the text blocks
                    for l in b["lines"]:  # iterate through the text lines
                        for s in l["spans"]:  # iterate through the text spans
                            font_color = s["color"]
                            text = s["text"]
                                            
                            # Convert the 32-bit color integer to an RGB tuple
                            red = (font_color >> 16) & 0xFF
                            '''  It shifts the 32-bit color integer 16 bits to the right, isolating the red component. 
                            The & 0xFF operation is used to mask any extra bits and 
                            ensure that the value is within the range 0-255.'''

                            green = (font_color >> 8) & 0xFF
                            '''it shifts the color integer 8 bits to the right to extract the green component and 
                            applies a masking operation to keep it within the range 0-255.'''

                            blue = font_color & 0xFF
                            ''' This directly extracts the blue component and ensures it is within the range 0-255.'''
                            
                            # Convert the RGB color to a hex format
                            hex_color = "#{:02X}{:02X}{:02X}".format(red, green, blue)
                            
                            text_color_data.append({ "Text": text, "Hex_Color": hex_color})

            pdf_document.close()

            return True,text_color_data
        
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)

            return False, text_color_data
            


 


        
    
    
        
    
    