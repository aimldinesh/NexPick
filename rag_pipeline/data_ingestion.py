# -------------------------------------------
# 📦 Imports
# -------------------------------------------
from langchain_astradb import AstraDBVectorStore  # For storing embeddings in AstraDB
from langchain_huggingface import (
    HuggingFaceEndpointEmbeddings,
)  # For generating embeddings via HuggingFace API
from rag_pipeline.data_converter import (
    DataConverter,
)  # Custom converter to format CSV data into documents
from rag_pipeline.config import (
    Config,
)  # Configuration settings (API keys, model names, etc.)


# -------------------------------------------
# 📥 Data Ingestor Class
# -------------------------------------------
class DataIngestor:
    def __init__(self):
        # Initialize embedding model using HuggingFace endpoint
        self.embedding = HuggingFaceEndpointEmbeddings(model=Config.EMBEDDING_MODEL)

        # Initialize AstraDB vector store for document storage
        self.vstore = AstraDBVectorStore(
            embedding=self.embedding,
            collection_name="flipkart_database",
            api_endpoint=Config.ASTRA_DB_API_ENDPOINT,
            token=Config.ASTRA_DB_APPLICATION_TOKEN,
            namespace=Config.ASTRA_DB_KEYSPACE,
        )

    def ingest(self, load_existing=True):
        """
        Load existing vector store or ingest new documents from CSV.
        """
        if load_existing:
            # If documents are already ingested, return the existing vector store
            return self.vstore

        # Convert CSV data to LangChain Document format
        docs = DataConverter("data/flipkart_product_review.csv").convert()

        # Add documents to the AstraDB vector store
        self.vstore.add_documents(docs)

        # Return the vector store for downstream use
        return self.vstore
