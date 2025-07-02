from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List
from langchain_core.documents import Document


#Extract Data From the PDF File
def load_pdf_file(data: str) -> List[Document]:
    """
    Extract data from PDF files in a directory.
    
    Args:
        data (str): Path to directory containing PDF files
        
    Returns:
        List[Document]: List of loaded documents
        
    Raises:
        ValueError: If directory doesn't exist or contains no PDF files
    """
    import os
    if not os.path.exists(data):
        raise ValueError(f"Directory {data} does not exist")
    
    loader = DirectoryLoader(data,
                            glob="*.pdf",
                            loader_cls=PyPDFLoader)

    documents = loader.load()
    
    if not documents:
        raise ValueError(f"No PDF files found in directory {data}")
    
    return documents



#Split the Data into Text Chunks
def text_split(extracted_data: List[Document]) -> List[Document]:
    """
    Split documents into smaller text chunks for better embedding performance.
    
    Args:
        extracted_data (List[Document]): List of documents to split
        
    Returns:
        List[Document]: List of text chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    text_chunks = text_splitter.split_documents(extracted_data)
    return text_chunks



#Download the Embeddings from HuggingFace 
def download_hugging_face_embeddings():
    """
    Download and initialize HuggingFace embeddings model.
    
    Returns:
        HuggingFaceEmbeddings: Initialized embeddings model
    """
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    return embeddings