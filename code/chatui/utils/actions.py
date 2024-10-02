
from typing import List

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_community.document_loaders import UnstructuredWordDocumentLoader, PyPDFLoader, TextLoader

from chatui.utils import database

from chatui.prompts import prompts_common, prompts_phi3
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents.refine import RefineDocumentsChain
from langchain.chains.llm import LLMChain
import os

root = os.path.join(os.path.dirname(__file__), "../../../")
feedback_path = os.path.join(root, "files", "feedback")

    

def infer_email_chain(llm):
    prompt = PromptTemplate(
        template=prompts_common.email_prompt,
        input_variables=["prompt"],
    )

    chain = prompt | llm | StrOutputParser()
    return chain


# retrieve the requirements from huge documents
def retrieve_requirements():
    question = prompts_common.retrieve_requirements_prompt

    retriever = database.get_retriever()
    documents = retriever.invoke(question)

    print("retrieved documents:", documents)
    return documents


def extract_requirements(documents, llm):
    content = [doc.page_content for doc in documents]
    if len(content) == 1:
        pr = prompts_phi3.extract_requirements_prompt
    else:
        pr = prompts_phi3.extract_requirements_prompt_multiple
    documents = " ".join(content)
    prompt = PromptTemplate(
        template=pr,
        input_variables=["documents"],
    )
    chain = prompt | llm | JsonOutputParser()
    requirements = chain.invoke({"documents": documents})
    print("requirements:", requirements)
    print("type:", type(requirements))
    return requirements


# Summary of student assignment (Essay / Report)
def summarize_documents(documents, llm):

    document_prompt = PromptTemplate(
        input_variables=["page_content"],
        template="{page_content}"
    )

    document_variable_name = "document"
 
    prompt = prompts_phi3.first_summarize_prompt
    first_prompt = PromptTemplate(
        input_variables=["document"],
        template=prompt
    )

    initial_llm_chain = LLMChain(llm=llm, prompt=first_prompt)

    initial_response_name = "previous"

    prompt_refine = prompts_phi3.next_summarize_prompt
    next_prompt = PromptTemplate(
        input_variables=["previous", "document"],
        template=prompt_refine
    )

    refine_llm_chain = LLMChain(llm=llm, prompt=next_prompt)
    chain = RefineDocumentsChain(
        initial_llm_chain=initial_llm_chain,
        refine_llm_chain=refine_llm_chain,
        document_prompt=document_prompt,
        document_variable_name=document_variable_name,
        initial_response_name=initial_response_name,
        input_key="page_content",
    )

    response = chain.invoke({"page_content": documents})

    print("summary", response)
    return response['output_text']

def get_doc_splits(file_path):
    if file_path.endswith(".pdf"):
        doc = [item for item in PyPDFLoader(file_path).load()]
    elif file_path.endswith((".docx", ".doc")):
        doc = [item for item in UnstructuredWordDocumentLoader(file_path).load()]
    elif file_path.endswith(".txt"):
        doc = TextLoader(file_path).load()
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=7000, chunk_overlap=0
    )
    doc_splits = text_splitter.split_documents(doc)
    return doc_splits


def get_feedback(criteria, file_path, llm):
    database.upload_assignment(file_path)
    assignment_retriever = database.get_assignment_retriever()
    documents = assignment_retriever.invoke(criteria)
    text = [doc.page_content for doc in documents]
    documents = " ".join(text)
    print('documents:', documents)
    prompt = PromptTemplate(
        template=prompts_phi3.feedback_prompt,
        input_variables=["criteria", "document"],
    )
    chain = prompt | llm | JsonOutputParser()
    response = chain.invoke({"criteria": criteria, "document": documents})
    return response

def get_feedback2(criteria, file_path, llm):
    database.upload_assignment(file_path)
    assignment_retriever = database.get_assignment_retriever()
    documents = assignment_retriever.invoke(criteria)
    text = [doc.page_content for doc in documents]
    documents = " ".join(text)
    print('documents:', documents)
    prompt = PromptTemplate(
        template=prompts_phi3.feedback_prompt,
        input_variables=["criteria", "document"],
    )
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"criteria": criteria, "document": documents})
    return response

def create_feedback(criteria, file_path, llm):
    response = get_feedback2(criteria, file_path, llm)
    file_name = os.path.basename(file_path).split('/')[-1]
    txt_file = file_name.split('.')[0] + ".txt"

    with open(os.path.join(feedback_path, txt_file), "w") as f:
        f.write(response)

def create_all_feedback(criterias, file_paths, llm):
    criteria = ""
    for i in range(len(criterias)):
        criteria += str(i+1) + ") " + criterias[i] + "\n"
    for file_path in file_paths:
        create_feedback(criteria, file_path, llm)

def get_text_from_file(file_path):
    if file_path.endswith(".pdf"):
        doc = [item.page_content for item in PyPDFLoader(file_path).load()]
        doc = "\n".join(doc)
    elif file_path.endswith((".docx", ".doc")):
        doc = UnstructuredWordDocumentLoader(file_path, mode='single').load()
        doc = [item.page_content for item in doc]
        doc = "\n".join(doc)
    elif file_path.endswith(".txt"):
        doc = [item.page_content for item in TextLoader(file_path).load()]
        doc = "\n".join(doc)

    print(doc)
    return doc



def find_related_files_from_email(email, files, llm):
    prompt = PromptTemplate(
        template=prompts_phi3.find_related_files_from_email_prompt,
        input_variables=["email", "files"],
    )
    chain = prompt | llm | JsonOutputParser()
    response = chain.invoke({"email": email, "files": files})
    sender = response['sender']
    email_address = response['email_address']
    title = response['title']
    content = response['content']
    result = prompts_common.email_result_format.format(
        sender=sender, email_address=email_address, title=title, content=content
    )
    related_files = response['related_files']
    return result, related_files


def generate_response_email(email, response, llm):
    prompt = PromptTemplate(
        template=prompts_phi3.generate_response_email_prompt,
        input_variables=["email", "feedback"],
    )
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"email": email, "feedback": response})
    return response