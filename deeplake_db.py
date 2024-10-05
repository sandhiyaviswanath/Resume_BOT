from deeplake.core.vectorstore import VectorStore
import logging


class DeeplakeDB:
    logger                 = logging.getLogger(__name__)
    EMPTY_LIST = []
    EMPTY_STR = ''

    def create_deeplake_database(self,resume_text,vectors,dataset_path):
        try:
            vector_store = VectorStore(
            path = dataset_path,overwrite=True
                )

            vector_store.add(text = resume_text, 
                            embedding = vectors, 
                            metadata = None,
            )
            return vector_store
        
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            print(e)
            return self.EMPTY_LIST

    def vector_search(self,vector_store,jd_embeddings):
        try:
            data =vector_store.search(embedding = jd_embeddings )
            return data
        
        except Exception as e:
            self.logger.critical(f'Error due to {e}', exc_info=True)
            return self.EMPTY_STR
