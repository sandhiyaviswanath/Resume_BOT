from pathlib import Path
from datetime import datetime, time
import logging
import os
import shutil

class osProcessor():
 
    logger = logging.getLogger(__name__)

    NULL_VALUE = 0
    EMPTY_STR = ''
 
    PARENT_DIR_IDX = -2
    GRAND_PARENT_DIR_IDX = -3
  
    QUALIFIED_FILE_EXTENSIONS = ('.pdf', '.docx', '.doc')
 
    def get_code_dir(self):
        try:
            folder = str(Path(__file__).resolve().parent)
            return True, folder

        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            return False, self.EMPTY_STR

    def get_file_extension(self, file_name):
        try:
            return True, str(Path(file_name).suffix)
 
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
 
            return False, self.EMPTY_STR
 
    def get_file_stem(self, file_name):
        try:
            return True, str(Path(file_name).stem)
 
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            return False, self.EMPTY_STR
 
    def get_file_size(self, qual_file_name):
        try:
            return True, Path(qual_file_name).stat().st_size
 
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)

            return False, self.NULL_VALUE
 
    def join_paths(self, file_name, *directory) :
        try:
            return True, str(Path(*directory) / Path(file_name))
 
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            return False, self.EMPTY_STR
 
    def get_parent_dirs_for_sql_path(self, qual_file_name_only, file_name):
        try:
            parent_dirname = Path(qual_file_name_only).parts[self.PARENT_DIR_IDX]
            grand_parent_dirname = Path(qual_file_name_only).parts[self.GRAND_PARENT_DIR_IDX]

            file_name = Path(qual_file_name_only).name

            parent_qual_file_name = Path(grand_parent_dirname) / parent_dirname / file_name

            return True, str(parent_qual_file_name)

        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)

            return False, self.EMPTY_STR
 
    def get_parent_dir(self, directory_or_qual_file_name):
        try:
            return True, str(Path(directory_or_qual_file_name).parent)
 
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
 
            return False, self.EMPTY_STR
 
    def create_dir_if_not_exists(self, directory):
        try:
            if not Path(directory).exists():
                Path(directory).mkdir(parents=True, exist_ok=True) # exist_ok=True does not raise Exception if directory already exists
 
            return True, str(Path(directory).resolve())
 
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
 
            return False, self.EMPTY_STR
 
    def create_working_dirs(self, qual_Base_file_name, folder_dict):
        try:
            for folder in folder_dict:
                base_working_dir = Path(qual_Base_file_name) / folder
                folder_dict[folder] = base_working_dir
 
                _ = self.create_dir_if_not_exists(base_working_dir)
 
            return True, folder_dict
 
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            return False, folder_dict
 
    def check_file_validity(self, qual_file_name):
        try:
            file_extension_status, file_extension = self.get_file_extension(qual_file_name)
            file_size_status, file_size = self.get_file_size(qual_file_name)
 
            if not (file_extension_status and file_size_status):
                return False
 
            if file_size <= 0:
                return False
 
            elif file_extension in self.QUALIFIED_FILE_EXTENSIONS:
                return True
 
            else:
                return False

        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
 
            return False

    def move_bad_files(self, list_bad_files, bad_file_dir):
        try:
            count = 0
            for qual_bad_file_name in list_bad_files:
                qual_src_bad_file_path = Path(qual_bad_file_name)
                qual_destination_file_name = Path(bad_file_dir) / Path(qual_bad_file_name).name
 
                qual_src_bad_file_path.rename(qual_destination_file_name)
 
                count += 1
 
            self.logger.info(f'{count} bad files moved to {bad_file_dir}')
 
            return True
 
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
 
            return False
 
    def get_list_all_files_in_dir(self, src_directory):
        try:
            src_directory = Path(src_directory)
            list_qual_file_names = [str(qual_file_name) for qual_file_name in src_directory.iterdir() if '~$' not in str(qual_file_name)]

            return True, list_qual_file_names
 
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)

            return False, list_qual_file_names
 
    def get_qual_file_name_no_extension(self, qual_file_name):
        try:
            return True, Path(qual_file_name).with_suffix('')

        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)

            return False, self.EMPTY_STR

    def get_new_name(self, qual_file_name_no_extension, file_extension):
        try:
            MAX_FILE_NUM_DIGIT = 3
            counter=''
            num_counter = 0

            while Path(fr'{qual_file_name_no_extension}{counter}{file_extension}').exists():
                num_counter += 1
                counter = str(num_counter).zfill(MAX_FILE_NUM_DIGIT)

            return True, fr'{qual_file_name_no_extension}{counter}{file_extension}'

        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
 
            return False, self.EMPTY_STR
 
    def save_file(self, file_doc_obj, qual_file_name_no_extension, file_extension):
        try:
            status, qual_file_name = self.get_new_name(qual_file_name_no_extension, file_extension)
 
            if not status:
                return False
 
            file_doc_obj.save(qual_file_name)
 
            return True
 
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
 
            return False
       
    def get_default_date(self):
        try:
            return datetime.fromtimestamp(0.0).strftime("%Y-%m-%d %H:%M:%S")
 
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
 
            return self.EMPTY_STR
 
    def get_current_date_time(self):
        try:
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
 
            return True, formatted_datetime
 
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            return False, self.get_default_date()
 
    def wait_till_fileExists_with_nonZero_fileSize(self, qual_file_name, time_delay, iterations):
        try:
            iter_counter = iterations
            i = 0
            while i <= iter_counter:
                if Path(qual_file_name).exists() and Path(qual_file_name).stat().st_size > 0:
                    break
                else:
                    time.sleep(time_delay)
                    i+=1
 
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)

    def create_path_name(self,destination_folder,file_name,extension):
        number_count=''
        try:
            while os.path.exists(fr'{destination_folder}\{file_name}_{number_count}.{extension}'):
                if number_count == '':
                    number_count = 1
                else:
                    number_count +=1
            return fr'{destination_folder}\{file_name}_{number_count}.{extension}'
        except:
            return self.EMPTY_STR
        
    def get_fileName(self, file_path):
        try:
            file_name = os.path.basename(file_path)
            name = os.path.splitext(file_name)[0]
            extension=os.path.splitext(file_name)[1]
            return True,name,extension
        except:
            return False,name,extension 
        
    def delete_folder(self,folder_path):
        try:
            shutil.rmtree(folder_path)
            print(f"Folder '{folder_path}' and all its contents have been deleted successfully.")
        except OSError as e:
            print(f"Error: {e.strerror}")