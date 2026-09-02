import streamlit as st
import os
from dotenv import load_dotenv

# Page configuration MUST be the absolute first Streamlit command executed
st.set_page_config(page_title="Kumaran Parvatham AI Agent", page_icon="💼", layout="centered")

# Immediately render the interface titles so the recruiter doesn't see a blank page
st.title("💼 Kumaran Parvatham")
st.subheader("AI Executive Talent Agent")
st.write(
    "Welcome! I am Kumaran's autonomous career agent. You can ask me anything about his "
    "24+ years of experience across Banking, Fintech, Payments, Enterprise Transformation, "
    "or his architectural design of the Agent Certification Framework (ACF)."
)

# Load environment secrets
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    st.error("Missing OpenAI API Key! Please verify your .env configuration file.")
    st.stop()

# Ensure the data directory exists and is visible to the interpreter path
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "profile_data"))
if not os.path.exists(DATA_DIR):
    st.error(f"Critical Error: Data folder not found at path: {DATA_DIR}. Please check your directories.")
    st.stop()

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Cache the RAG initialization logic with an interactive loader notification
@st.cache_resource
def initialize_rag_pipeline(data_path):
    # 1. Load data explicitly using the native, lightweight TextLoader class
    loader = DirectoryLoader(data_path, glob="**/*.md", loader_cls=TextLoader)
    docs = loader.load()
    
    if not docs:
        raise ValueError(f"No profile documents (.md files) found inside the {data_path} target folder.")
    
    # 2. Chunk text logically
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)
    
    # 3. Embed and store vectors
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # 4. Initialize LLM Model
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
    
    # 5. Executive Persona Prompt Guardrails
    system_prompt = (
        "You are the autonomous, professional Executive Talent Agent for Kumaran Parvatham.\n"
        "Your objective is to help recruiters, hiring managers, and ATS reviewers evaluate Kumaran's fit "
        "for banking, fintech, payments, and transformation leadership positions.\n\n"
        "CRITICAL GUARDRAILS:\n"
        "- Base your answers strictly and exclusively on the verified profile context provided below.\n"
        "- If a recruiter asks a question about skills, metrics, or experiences that are not explicit in Kumaran's "
        "context, state professionally that the information is not in his primary dossier and offer to connect them directly.\n"
        "- NEVER invent or hallucinate metrics, dates, or technical skills.\n"
        "- Keep responses punchy, articulate, and executive-level.\n\n"
        "CONVERSION STRATEGY:\n"
        "At the end of every answer, if relevant, seamlessly add a brief, single-sentence soft closing text providing Kumaran's "
        "direct email (Kumaran.alchemist@gmail.com) or contact (+91 96000 57231) for scheduling an exploratory call.\n\n"
        "Context Dossier:\n"
        "{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, combine_docs_chain)

# Initialize pipeline with standard UI handling
try:
    with st.spinner("Initializing executive dossier vector indexes..."):
        agent_engine = initialize_rag_pipeline(DATA_DIR)
except Exception as e:
    st.error(f"Pipeline Execution Error: {e}")
    st.stop()

# Initialize session message arrays
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation histories
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capture user interaction
if recruiter_query := st.chat_input("Ask me about Kumaran's portfolio scales, tech stacks, or availability..."):
    with st.chat_message("user"):
        st.markdown(recruiter_query)
    st.session_state.messages.append({"role": "user", "content": recruiter_query})
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing executive dossier..."):
            response = agent_engine.invoke({"input": recruiter_query})
            answer = response["answer"]
            st.markdown(answer)
            
    st.session_state.messages.append({"role": "assistant", "content": answer})
