from Services.vector_services import chroma_services

class Retrivals:
    top = 12
    def chroma_query(
        self,query:str,
        collection_name:str
    ):
        """
        chroma_query : Retrive 12 top result from chromadb from a specific collection
        return : {
                    'ids': [['id1', 'id2', 'id3']],
                    'documents': [['doc1 text', 'doc2 text', 'doc3 text']],
                    'metadatas': [[
                        {'source': 'file1.pdf'},
                        {'source': 'file2.pdf'},
                        {'source': 'file3.pdf'}
                    ]],
                    'distances': [[0.12, 0.25, 0.40]],
                    'embeddings': None
                }
        """
        try:
            client = chroma_services.get_chroma_client()
            collection = client.get_collection(collection_name)
        except Exception as e:
            print(f"Exception Ocuure while getting chromaclient or collection {e}")
        
        result = collection.query(
            query_texts=query,
            n_results=Retrivals.top
        )

        print("Retrive done from vector store")
        return result

retrival = Retrivals()
