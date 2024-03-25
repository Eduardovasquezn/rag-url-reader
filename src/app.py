
import streamlit as st
from langchain_community.vectorstores.faiss import FAISS

from common.utils import data_ingestion, get_embeddings, build_vector_store_database, get_llm, get_response_llm


def main():
    # Configure the settings of the webpage
    st.set_page_config(page_title="Chat with Websites", page_icon= "🧊", layout="wide")

    # Add a header
    st.header("Chat with websites using Google Palm and Gemini-Pro💬🤖")

    # Input question from the user
    user_question = st.text_input("Ask a question from the URLs")

    # Vertex AI - Google Palm text embeddings
    embeddings = get_embeddings()

    # Create a sidebar
    with st.sidebar:
        # Title of the sidebar
        st.title("News Articles URL:")

        # List of urls
        urls = []

        for i in range(5):
            url = st.sidebar.text_input(f"URL {i+1}")
            # Append URLs if provided
            if url:
                urls.append(url)

        if st.button("Process URLs"):
            with st.spinner("Data Ingestion...Started...✅✅✅"):
                # Ingest data
                docs = data_ingestion(urls = urls)
                # Create vector store database
                build_vector_store_database(documents = docs, embeddings = embeddings)
                st.success("Done")

    if st.button("Google Palm Output"):
        with st.spinner("Thinking"):
            # Load data
            faiss_index = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
            # Load LLM
            llm  = get_llm(model_name = "text-bison@002")

            st.write(get_response_llm(llm, faiss_index, user_question))

            st.success("Done")
    elif st.button("Gemini-Pro Output"):
        with st.spinner("Thinking"):
            # Load data
            faiss_index = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
            # Load LLM
            llm = get_llm(model_name="gemini-pro")

            st.write(get_response_llm(llm, faiss_index, user_question))

            st.success("Done")

if __name__ == "__main__":
    main()