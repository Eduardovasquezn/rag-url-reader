from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import VertexAIEmbeddings, VertexAI
from dotenv import load_dotenv
import os
import google.generativeai as genai
from langchain_community.vectorstores import FAISS

google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)


def data_ingestion(urls):

    loader = WebBaseLoader(urls)

    # Load html
    documents = loader.load()

    # Text splitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                   chunk_overlap=200)

    # Split data into chunks
    chunks = text_splitter.split_documents(documents)

    return chunks

def get_embeddings():
    # Model to get embeddings
    embeddings = VertexAIEmbeddings(model_name="textembedding-gecko@003")
    return embeddings

def build_vector_store_database(documents, embeddings):
    vector_store = FAISS.from_documents(documents=documents, embedding=embeddings)
    # Location where the vector store database is saved
    vector_store.save_local("faiss_index")

def get_llm(model_name):
    llm = VertexAI(model_name=model_name)
    return llm

def get_response_llm(llm, vector_store, query):
    prompt_template = """
    Human: Answer the question as detailed as possible from the provided context, make sure to provide all the details. 
        Don't exceed 250 words on the explanation. If you don't know the answer, just say that you don't know, 
        don't try to make up an answer.\n

        Context:\n {context}?\n
        Question: {question}

        Assistant:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=['context', 'question'])

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": 3}
        ),
        chain_type="stuff",
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}

    )
    answer = qa({"query": query})

    return answer['result']