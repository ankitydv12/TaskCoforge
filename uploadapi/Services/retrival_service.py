from Services.vector_services import chroma_services

class Retrivals:
    def chroma_query(
        self,query:str,
        collection_name:str,top:int
    ):
        client = chroma_services.get_chroma_client()
        #TODO: Handle if collection name is not present
        
        collection = client.get_collection(collection_name)

        result = collection.query(
            query_texts=query,
            n_results=top
        )

        print("Retriving done")
        return result

retrival = Retrivals()
