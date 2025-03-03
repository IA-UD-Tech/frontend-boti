"""
Service for interacting with language models.
"""

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from deustogpt.config import OPENAI_API_KEY

class LLMService:
    def __init__(self, personality=None):
        """
        Initialize the LLM service with optional personality prompt.
        
        Args:
            personality (str): Optional personality/prompt template for the LLM
        """
        self.setup_chain(personality)
        
    def setup_chain(self, personality=None):
        """
        Configure the LangChain components for the chat service.
        
        Args:
            personality (str): Optional personality prompt
        """
        prompt_template = personality if personality else """Eres un asistente virtual muy amable y amigable. Actualmente mantienes una conversación con un humano.
Responde a sus preguntas de forma cordial y con un toque de humor.

Historial: {chat_history},
Humano: {question}
AI:"""
        
        self.prompt = PromptTemplate(
            input_variables=["chat_history", "question"],
            template=prompt_template
        )
        self.llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY)
        self.memory = ConversationBufferWindowMemory(memory_key="chat_history", k=4)
        self.chain = LLMChain(
            llm=self.llm,
            memory=self.memory,
            prompt=self.prompt
        )
    
    def generate_response(self, question):
        """
        Generate an AI response based on the user's question.
        
        Args:
            question (str): User's question
            
        Returns:
            str: AI's response
        """
        return self.chain.predict(question=question)
        
    def add_to_memory(self, user_input, ai_response):
        """
        Add an interaction to the conversation memory.
        
        Args:
            user_input (str): User's message
            ai_response (str): AI's response
        """
        self.memory.chat_memory.add_user_message(user_input)
        self.memory.chat_memory.add_ai_message(ai_response)