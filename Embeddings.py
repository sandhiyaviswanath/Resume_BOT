from openai import OpenAI
import logging


class Embedding():

    logger                 = logging.getLogger(__name__)
    EMPTY_LIST = []    

    def create_embeddings_for_jd(self,jd_text):
        try:
            client = OpenAI()

            embeddings = client.embeddings.create(
            model="text-embedding-ada-002",
            input=jd_text,
            encoding_format="float"
            )
            vectors = [embedding.embedding for embedding in embeddings.data]
            return vectors
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            return self.EMPTY_LIST

    def create_embeddings_for_resumes(self,resume_texts):
        try:
            all_embeddings = []
            batch_size = min(len(resume_texts), 5)  # Set batch size to maximum of 6 or length of resume_texts
            num_complete_batches = len(resume_texts)//batch_size  # Number of complete batches
            remaining_texts = len(resume_texts)%batch_size  # Number of texts remaining after complete batches
        
            client = OpenAI(api_key="your API KYE")
            
            # Process complete batches
            for batch_index in range(num_complete_batches):
                start_index = batch_index * batch_size
                end_index = (batch_index + 1) * batch_size
                batch_texts = resume_texts[start_index:end_index]

                embeddings = client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=batch_texts,
                    encoding_format="float"
                )
            
                all_embeddings.extend(embeddings)

            # Process remaining texts
            if remaining_texts > 0:
                remaining_texts_batch = resume_texts[-remaining_texts:]
                embeddings = client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=remaining_texts_batch,
                    encoding_format="float"
                )
                all_embeddings.extend(embeddings)
            return all_embeddings
        
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            return self.EMPTY_LIST
