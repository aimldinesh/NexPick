import pandas as pd
from langchain_core.documents import Document


class DataConverter:
    """
    A simple utility to convert product reviews from a CSV file into LangChain Document objects.
    """

    def __init__(self, file_path: str):
        """
        Initializes the DataConverter with the path to the CSV file.

        Args:
            file_path (str): Path to the CSV file containing product reviews.
        """
        self.file_path = file_path

    def convert(self):
        """
        Reads the CSV file and converts each row into a LangChain Document.

        Returns:
            List[Document]: A list of Document objects with review as content and product title as metadata.
        """
        # Read the CSV file and select only the required columns
        df = pd.read_csv(self.file_path)[["product_title", "review"]]

        # Convert each row to a Document object
        docs = [
            Document(
                page_content=row["review"],  # Review content
                metadata={
                    "product_name": row["product_title"]
                },  # Metadata includes product title
            )
            for _, row in df.iterrows()
        ]

        return docs
