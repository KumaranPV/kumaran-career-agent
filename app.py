import streamlit as st
import os
from dotenv import load_dotenv

# Page configuration
st.set_page_config(page_title="Kumaran Parvatham AI Agent", page_icon="💼", layout="wide")

# Title and Header Layout
st.title("💼 Kumaran Parvatham")
st.subheader("AI Executive Talent Agent")
st.write(
    "Welcome! I am Kumaran's autonomous career agent. You can ask me questions about his "
    "24+ years of experience across Banking, Fintech, Payments, Enterprise Transformation, "
    "or use the **Job Matcher** tool to evaluate his fit for your open role instantly."
)

# Load secrets
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    st.error("Missing OpenAI API Key! Please verify your .env configuration file.")
    st.stop()

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

@st.cache_resource
def initialize_rag_pipeline(data_path):
    loader = DirectoryLoader(data_path, glob="[bepf]*.md", loader_cls=TextLoader)
    docs = loader.load()
    if not docs:
        raise ValueError(f"No profile documents (.md files) found at path: {data_path}")
    
    # Bypasses character splitting entirely to prevent layout truncation
    chunks = docs 
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0) # Temperature 0 forces strict copy-paste behavior
    return retriever, llm

try:
    retriever, llm = initialize_rag_pipeline(DATA_DIR)
except Exception as e:
    st.error(f"Pipeline Execution Error: {e}")
    st.stop()

col1, col2 = st.columns(2, gap="large")

# --- COLUMN 1: THE INTERACTIVE JOB MATCHER ---
with col1:
    st.markdown("### 🎯 Option A: Match Your Job Description")
    st.write("Paste your target JD below to get an instant, metric-backed gap analysis mapping Kumaran's career dossier directly to your requirements.")
    
    jd_input = st.text_area("Paste Job Description here:", height=300, placeholder="Looking for a Product/Transformation Executive with experience in banking core systems, scaling platforms, card-management system migrations...")
    
    if st.button("Analyze Role Fit ⚡️"):
        if jd_input.strip() == "":
            st.warning("Please paste a valid job description text to execute analysis.")
        else:
            with st.spinner("Executing structural alignment matrix..."):
                relevant_docs = retriever.invoke(jd_input)
                context_dossier = format_docs(relevant_docs)
                
                match_prompt = ChatPromptTemplate.from_messages([
                    ("system", (
                        "You are the senior executive talent agent for Kumaran Parvatham.\n"
                        "Analyze the pasted Job Description against Kumaran's context dossier below.\n"
                        "Provide a structured, executive-level output with these precise sections:\n"
                        "1. **Core Alignments**: Highlight specific metric-backed matches from his career (e.g., portfolio scale, 0-to-1 building, platform stabilization).\n"
                        "2. **Competency Translation**: If the JD requests a skill not explicitly in his dossier, professionally translate how his broader expertise mitigates this gap.\n"
                        "3. **Fit Summary & Call to Action**: A brief concluding sentence directing them to drop a line to Kumaran.alchemist@gmail.com.\n\n"
                        "Context Dossier:\n{context}"
                    )),
                    ("human", "Analyze this job description:\n{jd}")
                ])
                
                matcher_chain = match_prompt | llm | StrOutputParser()
                analysis_output = matcher_chain.invoke({"context": context_dossier, "jd": jd_input})
                
                st.markdown("---")
                st.markdown("### 📊 Custom Alignment Report")
                st.markdown(analysis_output)

# --- COLUMN 2: THE 24/7 CHAT CONSOLE ---
with col2:
    st.markdown("### 💬 Option B: General Recruiter Q&A")
    st.write("Ask specific exploratory questions about Kumaran's leadership competencies, technical tools, or project frameworks.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    chat_container = st.container(height=400)
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
    if recruiter_query := st.chat_input("Ask about portfolio scales, tech stacks, or availability..."):
        with chat_container:
            with st.chat_message("user"):
                st.markdown(recruiter_query)
        st.session_state.messages.append({"role": "user", "content": recruiter_query})
        
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are the autonomous, professional Executive Talent Agent for Kumaran Parvatham.\n"
                "Answer the user's question using ONLY the provided context dossier below.\n\n"
                "CRITICAL FORMATTING & SYNONYM DIRECTIVE:\n"
                "- The terms 'Kumaran', 'Kumaran Parvatham', 'him', 'he', and 'the candidate' are absolute synonyms.\n"
                "- If the user asks a broad summary question (e.g., 'Tell me about Kumaran', 'Who is Kumaran?', 'Who is this?', or requests an overview), "
                "you MUST extract and output his explicit 'Executive Persona' framework dossier verbatim from the context.\n"
                "- Preserve the exact layout structure, bullet points, headers, and specific formatting lines "
                "(such as 'Payments domain depth × Product/platform leadership × Enterprise transformation × Execution at scale').\n"
                "- Do NOT paraphrase or re-write these core structured profile blocks into paragraphs.\n\n"
                "At the end of your response, seamlessly add a single-sentence soft closing text providing Kumaran's direct email "
                "(Kumaran.alchemist@gmail.com) and contact (+91 96000 57231) for scheduling an exploratory call.\n\n"
                "Context Dossier:\n{context}"
            )),
            ("human", "{input}")
        ])

        
        context_docs = format_docs(retriever.invoke(recruiter_query))
        chat_chain = chat_prompt | llm | StrOutputParser()
        
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Analyzing dossier..."):
                    answer = chat_chain.invoke({"context": context_docs, "input": recruiter_query})
                    st.markdown(answer)
                    
        st.session_state.messages.append({"role": "assistant", "content": answer})
