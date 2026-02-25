<<<<<<< HEAD
import streamlit as st
from index import build_index
from query import get_answer
import tempfile
import os

st.title("📄 Chat With Your PDF")

# PDF Upload Section
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    
    # Build index when PDF is uploaded
    with st.spinner("Reading and indexing your PDF..."):
        build_index(tmp_path)
    
    st.success("PDF indexed! You can now ask questions.")
    
    # Chat Section
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Question input
    if question := st.chat_input("Ask a question about your PDF..."):
        # Display user question
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)
        
        # Get and display answer
        with st.chat_message("assistant"):
            with st.spinner("Searching PDF..."):
                answer = get_answer(question)
            st.write(answer)
        
=======
import streamlit as st
from index import build_index
from query import get_answer
import tempfile
import os

st.title("📄 Chat With Your PDF")

# PDF Upload Section
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    
    # Build index when PDF is uploaded
    with st.spinner("Reading and indexing your PDF..."):
        build_index(tmp_path)
    
    st.success("PDF indexed! You can now ask questions.")
    
    # Chat Section
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Question input
    if question := st.chat_input("Ask a question about your PDF..."):
        # Display user question
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)
        
        # Get and display answer
        with st.chat_message("assistant"):
            with st.spinner("Searching PDF..."):
                answer = get_answer(question)
            st.write(answer)
        
>>>>>>> c594a4355a8b416c0fb00172783ecad340aac84d
        st.session_state.messages.append({"role": "assistant", "content": answer})