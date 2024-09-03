import os

from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_text_splitters import CharacterTextSplitter
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain_community.vectorstores.pgvector import PGVector
import numpy as np
from os import getenv
from langchain_core.prompts import ChatPromptTemplate
import requests

API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
headers = {"Authorization": f"Bearer {getenv('HUGGINGFACEHUB_API_TOKEN')}"}

def get_embeddings(text):
    payload = {
	"inputs": {
	"source_sentence": text,
	"sentences": [
		text
	        ]
        },
    }
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        embeddings = response.json()
        print(embeddings)
        return embeddings
    else:
        raise Exception(f"Failed to get embeddings: {response.status_code}, {response.text}")



CONNECTION_STRING = getenv("DATABASE_URL")
COLLECTION_NAME = 'test_vectors'

model_kwargs = {'device': 'cpu'}
def vectorize(text, name):
    print("uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu")
    print(text)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs=model_kwargs)
    print(embeddings)
    print("zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz")
    query_result = embeddings.embed_query(text)
    print(query_result)
    return query_result


def vector2text(vector, question):
    print(vector)
    # llm from groq
    llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    groq_api_key=getenv('GROQ_API_KEY')
    )

    # create a qa chain
    qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector.as_retriever(),
    return_source_documents=True
    )

    response = qa_chain.invoke({"query": question})
    return response


def get_chat_completion(question, relevant_chunks):
    # Initialize the ChatGroq model
    chat = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    groq_api_key=getenv('GROQ_API_KEY')
    )
    
    
    system = "You are a helpful assistant."
    human = "{question}"
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    chain = prompt | chat
    response = chain.invoke({"question": f"Context: {relevant_chunks}\nQuestion: {question}\nAnswer:"})
    
    try:
        print(response)
        return response.content
    except TypeError as e:
        print(f"Error: {e}")

    
    # Combine context and question
    # prompt = f"Context: {relevant_chunks}\nQuestion: {question}\nAnswer:"
   
    # try:
    #     response = chat(prompt)
    #     print(response)
    # except TypeError as e:
    #     print(f"Error: {e}")
    