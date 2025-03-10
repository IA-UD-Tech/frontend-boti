import os
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from decouple import config
from langchain.memory import ConversationBufferWindowMemory

# Additional imports for document embedding
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Imports for Google OAuth
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests

# Imports for Supabase Logging and JWT decoding
from supabase import create_client, Client
import jwt
import json

class ChatApp:
    def __init__(self):
        self.setup_page()
        self.setup_decorations()
        self.api_key = config("OPENAI_API_KEY", default=os.getenv("OPENAI_API_KEY", ""))
        self.setup_chain()
        self.upload_dir = "uploaded_files"
        self.ensure_upload_dir()
        self.initialize_session_state()
        st.title("DeustoGPT")
        # Inicializa Supabase
        supabase_url = config("SUPABASE_URL")
        supabase_key = config("SUPABASE_KEY")
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.conversation_id = None  # Se establecerá tras la autenticación

    def setup_page(self):
        st.set_page_config(
            page_title="DeustoGPT",
            page_icon="🤖",
            layout="wide"
        )
    
    def setup_decorations(self):
        with open("front_end/static/chat_theme.html") as f:
            custom_css = f.read()
        st.markdown(custom_css, unsafe_allow_html=True)
    
    def setup_chain(self):
        self.prompt = PromptTemplate(
            input_variables=["chat_history", "question"],
            template="""Eres un asistente virtual muy amable y amigable. Actualmente mantienes una conversación con un humano.
Responde a sus preguntas de forma cordial y con un toque de humor.

Historial: {chat_history},
Humano: {question}
AI:"""
        )
        self.llm = ChatOpenAI(openai_api_key=self.api_key)
        self.memory = ConversationBufferWindowMemory(memory_key="chat_history", k=4)
        self.chain = LLMChain(
            llm=self.llm,
            memory=self.memory,
            prompt=self.prompt
        )
    
    def ensure_upload_dir(self):
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
    
    def initialize_session_state(self):
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "¡Hola! Soy DeustoGPT, tu asistente virtual. ¿En qué puedo ayudarte?"}
            ]
        if "embedded_documents" not in st.session_state:
            st.session_state.embedded_documents = {}
        # Almacenar token de Google después del login
        if "google_token" not in st.session_state:
            st.session_state.google_token = None

    def authenticate_user(self):
        """
        Maneja el flujo de autenticación mediante Google OAuth.
        Se espera un archivo 'client_secrets.json' en el directorio raíz.
        """
        if st.session_state.google_token:
            return True
        
        st.sidebar.subheader("Autenticación")
        cols = st.sidebar.columns([1, 4])
        with cols[0]:
            st.image("https://img.icons8.com/?size=512&id=17949&format=png", width=30)
        with cols[1]:
            if st.button("Iniciar sesión con Google", key="google_login"):
                flow = Flow.from_client_secrets_file(
                    'client_secrets.json',
                    scopes=["https://www.googleapis.com/auth/userinfo.profile",
                            "https://www.googleapis.com/auth/userinfo.email", "openid"],
                    redirect_uri='http://localhost:8501/oauth2callback'
                )
                auth_url, state = flow.authorization_url(prompt='consent', access_type='offline')
                st.session_state.google_oauth_state = state
                # Redirige automáticamente al usuario utilizando meta refresh
                st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}" />', unsafe_allow_html=True)
                st.stop()  # Detiene la ejecución para permitir el login
        
        # Procesa el código de respuesta en los parámetros de la URL
        query_params = st.query_params
        if "code" in query_params:
            code = query_params["code"][0]
            flow = Flow.from_client_secrets_file(
                'client_secrets.json',
                scopes=["https://www.googleapis.com/auth/userinfo.profile",
                        "https://www.googleapis.com/auth/userinfo.email", "openid"],
                redirect_uri='http://localhost:8501/oauth2callback'
            )
            flow.fetch_token(code=code)
            credentials = flow.credentials
            st.session_state.google_token = credentials.token
            st.sidebar.success("Autenticación correcta con Google")
            return True

        #TODO: Manejar errores de autenticación
        return True
        return False

    def get_google_user_id(self):
        """
        Decodifica el token de Google para extraer el ID de usuario.
        Se asume que el token sigue el formato JWT.
        """
        return "test_user"  # Temporalmente deshabilitado para pruebas
        token = st.session_state.google_token
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            return decoded.get("sub")
        except Exception as e:
            st.error("No se pudo decodificar el token de Google.")
            return None

    def upload_file(self):
        st.sidebar.title("Explorador de archivos")
        uploaded_file = st.sidebar.file_uploader("Sube un archivo")
        if uploaded_file is not None:
            save_path = os.path.join(self.upload_dir, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.sidebar.success(f"¡Archivo '{uploaded_file.name}' subido exitosamente!")

    def list_files(self):
        files = []
        for root, _, filenames in os.walk(self.upload_dir):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return files

    def get_icon(self, file_name):
        ext = os.path.splitext(file_name)[1].lower()
        if ext in ['.png', '.jpg', '.jpeg', '.gif']:
            return "🖼️"
        elif ext == '.pdf':
            return "📕"
        elif ext in ['.doc', '.docx']:
            return "📝"
        else:
            return "📄"

    def show_file_explorer(self):
        files = self.list_files()
        st.sidebar.subheader("Archivos")
        for file in files:
            file_name = os.path.basename(file)
            icon = self.get_icon(file_name)
            if st.sidebar.button(f"{icon} {file_name}", key=file):
                self.process_file(file, file_name)

    def process_file(self, file_path, file_name):
        # Cargar e incrustar el documento
        loader = UnstructuredFileLoader(file_path)
        documents = loader.load()  # Retorna una lista de Document
        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs = splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
        vectorstore = FAISS.from_documents(docs, embeddings)
        st.session_state.embedded_documents[file_name] = vectorstore
        
        # Mensaje de confirmación
        file_message = f"Documento '{file_name}' alimentado y listo para consultas."
        self.add_message("user", file_message)
        with st.chat_message("user"):
            st.write(file_message)
        
        # Generar una descripción breve del documento
        prompt_desc = f"Proporcione una breve descripción del documento '{file_name}', incluyendo sus detalles clave y un resumen."
        with st.chat_message("assistant"):
            with st.spinner("Alimentando documento y generando descripción..."):
                description_response = self.chain.predict(question=prompt_desc)
                st.write(description_response)
        self.add_message("assistant", description_response)
        
        # Serializa la información del documento para Supabase
        serialized_docs = [
            {"content": d.page_content, "metadata": d.metadata} for d in docs
        ]
        user_id = self.conversation_id or "unknown"
        self.supabase.table("embedded_documents").insert({
            "user_id": hash(user_id),
            "document_name": file_name,
            "documents": json.dumps(serialized_docs)
        }).execute()

    def add_message(self, role, content):
        st.session_state.messages.append({"role": role, "content": content})
        if role == "user":
            self.memory.chat_memory.add_user_message(content)
        elif role == "assistant":
            self.memory.chat_memory.add_ai_message(content)
        # Log the message in Supabase
        user_id = self.conversation_id or "unknown"
        try:
            response = self.supabase.table("messages").insert({
                "user_id": hash(user_id),
                "role": role,
                "content": content
            }).execute()
            if response.error is not None:
                st.error(f"Error al guardar mensaje en Supabase: {response.error}")
        except Exception as e:
            st.error(f"Error al guardar mensaje en Supabase: {str(e)}")
    
    def show_chat(self):
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    def process_chat_input(self):
        user_input = st.chat_input("Escribe aquí...")
        if user_input is not None and user_input.strip() != "":
            self.add_message("user", user_input)
            with st.chat_message("user"):
                st.write(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Cargando..."):
                    ai_response = self.chain.predict(question=user_input)
                    st.write(ai_response)
            self.add_message("assistant", ai_response)
    
    def run(self):
        # Ejecutar autenticación antes de continuar con la app
        if not self.authenticate_user():
            st.warning("Debes iniciar sesión con Google para continuar.")
            return
        
        # Establece el identificador de la conversación empleando el ID de usuario de Google
        self.conversation_id = self.get_google_user_id()
        if not self.conversation_id:
            st.error("No se pudo obtener el ID de usuario de Google.")
            return

        self.upload_file()
        self.show_file_explorer()
        self.show_chat()
        self.process_chat_input()

if __name__ == "__main__":
    app = ChatApp()
    app.run()