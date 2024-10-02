from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredWordDocumentLoader, PyPDFLoader, TextLoader
from langchain_chroma import Chroma
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from typing import Any, Dict, List
from langchain_huggingface import HuggingFaceEmbeddings
import os
import torch

cur = os.path.dirname(__file__)
root = os.path.join(cur, "../../../")
data_path = os.path.join(root, "data")

if torch.cuda.is_available():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", model_kwargs={'device': 'cuda'}, encode_kwargs={'device': 'cuda'})
elif torch.backends.mps.is_available():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", model_kwargs={'device': 'mps'}, encode_kwargs={'device': 'mps'})
else:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'}, encode_kwargs={'device': 'cpu'})


######## HANDLE REQUIREMENT FILES ########
def handle_text(documents: List[str]):

    docs = [TextLoader(document).load() for document in documents]
    docs_list = [item for sublist in docs for item in sublist]
    
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=250, chunk_overlap=0
    )
    doc_splits = text_splitter.split_documents(docs_list)

    return doc_splits
    
def handle_word(documents: List[str]):
    docs = [UnstructuredWordDocumentLoader(document).load() for document in documents]
    docs_list = [item for sublist in docs for item in sublist]
    
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=250, chunk_overlap=0
    )
    doc_splits = text_splitter.split_documents(docs_list)

    return doc_splits
    
def handle_pdf(documents: List[str]):
    """ This is a helper function for parsing the user inputted URLs and uploading them into the vector store. """
    docs = [PyPDFLoader(document).load() for document in documents]
    docs_list = [item for sublist in docs for item in sublist]
    
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=250, chunk_overlap=0
    )
    doc_splits = text_splitter.split_documents(docs_list)

    return doc_splits
    
def upload_files(files: List[str]):

    pdf_files = [file for file in files if file.lower().endswith('.pdf')]
    doc_files = [file for file in files if file.lower().endswith(('.docx', '.doc'))]
    txt_files = [file for file in files if file.lower().endswith('.txt')]

    # Now you can handle each type of file accordingly
    pdf_splits = handle_pdf(pdf_files)
    doc_splits = handle_word(doc_files)  
    txt_splits = handle_text(txt_files)  

    all_splits = pdf_splits + doc_splits + txt_splits  

    vectorstore = Chroma.from_documents(
        documents=all_splits,
        collection_name="rag-chroma",
        embedding=embeddings,
        persist_directory=data_path,
    )
    return vectorstore

def clear():
    """ This is a helper function for emptying the collection the vector store. """
    vectorstore = Chroma(
        collection_name="rag-chroma",
        embedding_function=embeddings,
        persist_directory=data_path,
    )
    
    vectorstore._client.delete_collection(name="rag-chroma")
    vectorstore._client.create_collection(name="rag-chroma")

def get_retriever(): 
    """ This is a helper function for returning the retriever object of the vector store. """
    vectorstore = Chroma(
        collection_name="rag-chroma",
        embedding_function=embeddings,
        persist_directory=data_path,
    )
    retriever = vectorstore.as_retriever()
    return retriever


######## HANDLE ASSIGNMENT FILES ########
def upload_assignment(file_path):
    
    if file_path.endswith(".pdf"):
        doc = [item for item in PyPDFLoader(file_path).load()]
    elif file_path.endswith((".docx", ".doc")):
        doc = UnstructuredWordDocumentLoader(file_path).load()
    elif file_path.endswith(".txt"):
        doc = TextLoader(file_path).load()
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=250, chunk_overlap=0
    )
    documents = text_splitter.split_documents(doc)
    vectorstore = Chroma(
        collection_name="assignment-rag-chroma",
        embedding_function=embeddings,
        persist_directory=data_path,
    )

    vectorstore._client.delete_collection(name="assignment-rag-chroma")

    vectorstore = Chroma.from_documents(
        documents=documents,
        collection_name="assignment-rag-chroma",
        embedding=embeddings,
        persist_directory=data_path,
    )

    return vectorstore

def get_assignment_retriever():
    vectorstore = Chroma(
        collection_name="assignment-rag-chroma",
        embedding_function=embeddings,
        persist_directory=data_path,
    )
    retriever = vectorstore.as_retriever()
    return retriever



def read_emails(text):
    """ This is a helper function for parsing the user inputted emails and uploading them into the vector store. """
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=7000, chunk_overlap=0
    )
    documents = text_splitter.split_documents([text])
    vectorstore = Chroma.from_documents(
        documents=documents,
        collection_name="email-rag-chroma",
        embedding=embeddings,
        persist_directory=data_path,
    )
    return vectorstore