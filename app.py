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
    
    chunks = docs 
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1) 
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
                        "You are the senior executive talent partner assessing Kumaran Parvatham against a pasted Job Description.\n"
                        "Analyze the pasted Job Description against Kumaran's context dossier below.\n"
                        "You must calculate and output an exact structured scorecard based strictly on the following guidelines:\n\n"
                        "CRITICAL STRUCTURAL SECTIONS TO GENERATE:\n"
                        "1. **Overall Fit Score**: Evaluate an explicit overall percentage (e.g., '91% — Strong Match') dynamically based on your analysis.\n"
                        "2. **Full Matches**: Bullet points listing clear overlaps (e.g., Payments/issuer processing, Product & platform leadership, etc.).\n"
                        "3. **Partial Matches**: Structural items needing slight verification (e.g., Full P&L ownership, specific local market experience, etc.).\n"
                        "4. **Gaps / Risks**: Honest assessments (e.g., No current EU/US work rights if outside India, or specified limitations derived from the JD vs context).\n"
                        "5. **Why the Score is X%**: Output a numerical breakdown mapping exactly to these categories:\n"
                        "   - Domain fit — X/25\n"
                        "   - Product leadership — X/25\n"
                        "   - Technology/platform depth — X/20\n"
                        "   - Commercial/P&L — X/15\n"
                        "   - Geography/regulatory fit — X/10\n"
                        "   - Work authorisation — X/10\n"
                        "   - *Ensure the sum of these fields matches your total generated percentage perfectly.*\n"
                        "6. **Recommendation**: Worth interviewing: YES/NO and a short 'Why' sentence stating if gaps are non-critical.\n"
                        "7. **Recommended Interview Focus**: Provide 3-4 highly specific question bullet points to guide the hiring team during their first interview clip (e.g., Clarify depth of full P&L ownership, Validate architecture choice frameworks, etc.).\n\n"
                        "Context Dossier:\n{context}"
                    )),
                    ("human", "Analyze this job description and produce the explicit scorecard framework output:\n{jd}")
                ])
                
                matcher_chain = match_prompt | llm | StrOutputParser()
                analysis_output = matcher_chain.invoke({"context": context_dossier, "jd": jd_input})
                
                st.markdown("---")
                st.markdown("### 📊 Custom Alignment Report")
                
                # Dynamic visual rendering for modern web UI utility
                if "91%" in analysis_output or "90%" in analysis_output or "Strong" in analysis_output:
                    st.success("🎯 Alignment Calculated: Highly Compatible Candidate Profile")
                elif "No" in analysis_output:
                    st.warning("⚠️ Alignment Calculated: Partial Fit Profile")
                    
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
                "CRITICAL CONVERSATIONAL DIRECTION:\n"
                "- Maintain a polished, articulate, professional executive tone.\n"
                "- CHRONOLOGICAL DENSITY CONTROL: Limit responses to exactly 2 or 3 high-impact thematic pillars maximum per answer to ensure punchiness.\n"
                "- PRODUCT LEADERSHIP ROLES REQUIREMENT: When asked about Product Leadership, Product Fit, or Innovation, you MUST explicitly anchor the response on his Current AI initiatives (ACF + Financial Orchestration), Entrepreneurial venture (YiPay), and Enterprise Scale track (Zeta).\n"
                "- P&L / FINANCIAL OWNERSHIP DIRECTIVE: If a recruiter explicitly asks if Kumaran has handled a 'P&L', 'Profit and Loss', 'budget management', or has 'full P&L ownership', you MUST output this specific statement verbatim: 'Kumaran has significant commercial, portfolio, budget, pricing, vendor-economics and business-development exposure, but the dossier does not demonstrate long-term end-to-end ownership of a standalone business P&L comparable to a GM. This should be explored in an interview if full P&L accountability is essential.' Do not summarize or alter this message.\n"
                "- TECHNICAL ARCHITECT QUERY DIRECTIVE: If the user asks if Kumaran is or was a 'technical architect', 'enterprise architect', 'solution architect', or asks about his role choosing technology stacks, you MUST output this exact response layout: 'No. His experience is stronger at product/platform and transformation leadership, working closely with architecture and engineering teams. While he serves as the End-to-End Product Builder for the Agent Certification Framework (ACF) and the Principal Architect/Solo Builder for his AI Core Financial Orchestration concept—collaborating directly with LLMs to inform code and configuration choices based on functional requirements—he structures these architectures from a product outcome lens. He has influenced major core structural decisions and can confidently discuss trade-offs, Non-Functional Requirements (NFRs), and system operating implications, but he should not be positioned as a traditional career enterprise architect.'\n"
                "- If the user asks for a broad summary overview (e.g., 'Tell me about Kumaran'), preserve his exact structured 'Executive Persona' block verbatim.\n"
                "- NEVER fabricate metrics, dates, or technical facts outside the provided dossier context.\n\n"
                "At the end of your response, seamlessly add a single-sentence soft closing text providing Kumaran's direct email "
