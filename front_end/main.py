import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from decouple import config
from langchain.memory import ConversationBufferWindowMemory
import os

prompt = PromptTemplate(
    input_variables=["chat_history", "question"],
    template="""You are a very kind and friendly AI assistant. You are
currently having a conversation with a human. Answer the questions
in a kind and friendly tone with some sense of humor.

chat_history: {chat_history},
Human: {question}
AI:"""
)

openai_api_key = config("OPENAI_API_KEY")
llm = ChatOpenAI(openai_api_key=openai_api_key)
memory = ConversationBufferWindowMemory(memory_key="chat_history", k=4)
llm_chain = LLMChain(
    llm=llm,
    memory=memory,
    prompt=prompt
)

st.set_page_config(
    page_title="DeutoGPT",
    page_icon="🤖",
    layout="wide"
)

st.title("DeustoGPT")

# Sidebar for file upload and file listing
st.sidebar.title("File Browser")
uploaded_file = st.sidebar.file_uploader("Upload a file")

# Ensure the upload directory exists
directory = "uploaded_files"
if not os.path.exists(directory):
    os.makedirs(directory)

# Save uploaded file
if uploaded_file is not None:
    save_path = os.path.join(directory, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success(f"File '{uploaded_file.name}' uploaded successfully!")

# Function to list files in a directory
def list_files(directory):
    files = []
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files

files = list_files(directory)

# Helper function to choose an icon based on file extension
def get_icon(file_name):
    ext = os.path.splitext(file_name)[1].lower()
    if ext in ['.png', '.jpg', '.jpeg', '.gif']:
        return "🖼️"
    elif ext == '.pdf':
        return "📕"
    elif ext in ['.doc', '.docx']:
        return "📝"
    else:
        return "📄"

st.sidebar.subheader("Files")
# Instead of drag and drop, we add a clickable button for each file.
# When a file is dropped, we add its message not just to session_state but also to the chain-memory.
for file in files:
    file_name = os.path.basename(file)
    icon = get_icon(file_name)
    if st.sidebar.button(f"{icon} {file_name}", key=file):
        file_message = f"File dropped: {file_name}"
        st.session_state.setdefault("messages", [])
        st.session_state.messages.append({"role": "user", "content": file_message})
        # Also update the chain memory with the dropped file message.
        memory.chat_memory.add_user_message(file_message)
        with st.chat_message("user"):
            st.write(file_message)

# Initialize messages in session state if not present.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Soy DeustoGPT, tu asistente virtual. ¿En qué puedo ayudarte?"}
    ]

# Display all messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_prompt = st.chat_input()

if user_prompt is not None and user_prompt.strip() != "":
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    memory.chat_memory.add_user_message(user_prompt)
    with st.chat_message("user"):
        st.write(user_prompt)
    
    # Only call the chain when text is provided.
    with st.chat_message("assistant"):
        with st.spinner("Loading..."):
            ai_response = llm_chain.predict(question=user_prompt)
            st.write(ai_response)
    new_ai_message = {"role": "assistant", "content": ai_response}
    st.session_state.messages.append(new_ai_message)
    memory.chat_memory.add_ai_message(ai_response)

# Only call the chain if the last message is from the user AND there is valid input.
if st.session_state.messages[-1]["role"] != "assistant" and user_prompt is not None and user_prompt.strip() != "":
    with st.chat_message("assistant"):
        with st.spinner("Loading..."):
            ai_response = llm_chain.predict(question=user_prompt)
            st.write(ai_response)
    new_ai_message = {"role": "assistant", "content": ai_response}
    st.session_state.messages.append(new_ai_message)
    memory.chat_memory.add_ai_message(ai_response)