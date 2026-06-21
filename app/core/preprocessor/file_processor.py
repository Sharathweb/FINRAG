from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader, UnstructuredPDFLoader, UnstructuredWordDocumentLoader
)
from conf import config
from utils.utils import logger

# Configure the splitter for English documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=900,        # Standard chunk size for embedding models
    chunk_overlap=200,      # Overlap helps maintain context between chunks
    separators=["\n\n", "\n", ".", " ", ""]
)

class FileProcesser:

    def __init__(self):
        logger.info("Successfully initialized file processor")

    def split_file_to_docs(self, file_path):
        logger.info("Starting file parsing. Larger files will take longer; please be patient...")
        file_type = file_path.split('.')[-1].lower()

        # Loaders are selected based on file extension
        if file_type == "txt":
            loader = TextLoader(file_path, autodetect_encoding=True)
        elif file_type == "pdf":
            # "fast" strategy extracts text layer directly without OCR
            loader = UnstructuredPDFLoader(file_path, strategy="fast")
        elif file_type == "docx":
            loader = UnstructuredWordDocumentLoader(file_path, mode="elements")
        else:
            raise TypeError("Unsupported file type. Currently only supports: [txt, pdf, docx]")

        # Load the document
        docs = loader.load()

        # Split documents using the unified English splitter
        logger.info(f"Number of documents before splitting: {len(docs)}")
        docs = text_splitter.split_documents(docs)
        logger.info(f"Number of documents after splitting: {len(docs)}")
        
        self.docs = docs
        return docs