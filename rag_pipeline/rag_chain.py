# -------------------------------------------
# 📦 Imports
# -------------------------------------------
from langchain_groq import ChatGroq
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from rag_pipeline.config import Config


# -------------------------------------------
# 🧠 RAGChainBuilder Class
# -------------------------------------------
class RAGChainBuilder:
    """
    Builds a complete Retrieval-Augmented Generation (RAG) pipeline with:
    - History-aware retriever
    - Question-answering document chain
    - In-memory session message history
    """

    def __init__(self, vector_store):
        # Initialize vector store and chat model
        self.vector_store = vector_store
        self.model = ChatGroq(model=Config.RAG_MODEL, temperature=0.5)

        # Store for managing session-wise chat history
        self.history_store = {}

    def _get_history(self, session_id: str) -> BaseChatMessageHistory:
        """
        Retrieve or initialize chat history for a given session ID.
        Enables session persistence across messages.
        """
        if session_id not in self.history_store:
            self.history_store[session_id] = ChatMessageHistory()
        return self.history_store[session_id]

    def build_chain(self):
        """
        Constructs and returns the full RAG chain with:
        - Contextual retriever
        - Prompt-aware QA chain
        - Message history support
        """

        # Create a retriever to fetch relevant documents (k=3)
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

        # Prompt for rephrasing follow-up queries using chat history
        context_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Given the chat history and user question, rewrite it as a standalone question.",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        # Prompt template for answering user questions based on context
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You're an e-commerce bot answering product-related queries using reviews and titles.
             Stick to context. Be concise and helpful.\n\nCONTEXT:\n{context}\n\nQUESTION: {input}""",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        # Build retriever that rewrites questions based on chat history
        history_aware_retriever = create_history_aware_retriever(
            self.model, retriever, context_prompt
        )

        # Document QA chain that combines documents and generates final answers
        question_answer_chain = create_stuff_documents_chain(self.model, qa_prompt)

        # Final RAG chain: combines retriever and QA chain
        rag_chain = create_retrieval_chain(
            history_aware_retriever, question_answer_chain
        )

        # Wrap the RAG chain with message history for session-aware conversations
        return RunnableWithMessageHistory(
            rag_chain,
            self._get_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
