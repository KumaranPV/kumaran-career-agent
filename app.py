import streamlit as st
import os
from dotenv import load_dotenv

# ==============================================================================
# 1. CORE PAGE CONFIGURATION (MUST BE FIRST STREAMLIT DIRECTIVE)
# ==============================================================================
st.set_page_config(page_title="Kumaran Parvatham AI Agent", page_icon="💼", layout="wide")

# Load environment configurations
load_dotenv()

# ==============================================================================
# 2. GLOBAL STORAGE: SYSTEM PROMPT BLOCKS
# ==============================================================================
SYSTEM_JOB_MATCHER_INSTRUCTION = """You are the senior executive talent partner assessing Kumaran Parvatham against a pasted Job Description.
Analyze the pasted Job Description against Kumaran's context dossier below.
You must calculate and output an exact structured scorecard based strictly on the following guidelines:

CRITICAL STRUCTURAL SECTIONS TO GENERATE:
1. **Overall Fit Score**: Evaluate an explicit overall percentage (e.g., '91% — Strong Match') dynamically based on your analysis.
2. **Full Matches**: Bullet points listing clear overlaps (e.g., Payments/issuer processing, Product & platform leadership, etc.).
3. **Partial Matches**: Structural items needing slight verification (e.g., Full P&L ownership, specific local market experience, etc.).
4. **Gaps / Risks**: Honest assessments (e.g., No current EU/US work rights if outside India, or specified limitations derived from the JD vs context).
5. **Why the Score is X%**: Output a numerical breakdown mapping exactly to these categories:
   - Domain fit — X/25
   - Product leadership — X/25
   - Technology/platform depth — X/20
   - Commercial/P&L — X/15
   - Geography/regulatory fit — X/10
   - Work authorisation — X/10
   - *Ensure the sum of these fields matches your total generated percentage perfectly.*
6. **Recommendation**: Worth interviewing: YES/NO and a short 'Why' sentence stating if gaps are non-critical.
7. **Recommended Interview Focus**: Provide 3-4 highly specific question bullet points to guide the hiring team during their first interview clip (e.g., Clarify depth of full P&L ownership, Validate architecture choice frameworks, etc.).

Context Dossier:
{context}"""

SYSTEM_CHAT_INSTRUCTION = """You are the autonomous, professional Executive Talent Agent for Kumaran Parvatham.
Answer the user's question using ONLY the provided context dossier below.

CRITICAL CONVERSATIONAL & MULTI-LAYER ROUTING DIRECTION:
- Maintain a polished, articulate, professional executive tone.
- CHRONOLOGICAL DENSITY CONTROL: Limit responses to exactly 2 or 3 high-impact thematic pillars maximum per answer to ensure punchiness.

STRICT THREE-LAYER VETTING EXTRACTION RULES:
- If a user asks any of your high-stakes vetting questions, look up the corresponding 'Topic' inside the context dossier.
- LAYER 1 (QUICK RESPONSE): By default, if the user asks a standard, direct question (e.g., 'Why did he leave Zeta?', 'How technical is he?', etc.), extract and output ONLY the word-for-word text found directly inside **'Layer 1 — Quick Response'** for that topic.
- LAYER 2 (DETAILED EXPLANATION): If the user's prompt explicitly asks for "details", "elaborate", "can you explain more", or "deep dive", you MUST extract and output the word-for-word text found inside **'Layer 2 — Detailed Explanation'** for that topic.
- LAYER 3 (SHOW ME EVIDENCE): If the user's prompt explicitly asks for "evidence", "metrics", "case studies", "records", or uses the phrase "show me the evidence", you MUST extract and output the complete text blocks found inside **'Layer 3 — Show me the evidence'** for that topic.

- NEVER output header labels like 'Layer 1' or 'Topic' to the screen. Speak the answer naturally.
- If the user asks for a broad summary overview (e.g., 'Tell me about Kumaran'), preserve his exact structured 'Executive Persona' block verbatim.
- NEVER fabricate metrics, dates, or technical skills outside the dossier context.

At the end of your response, seamlessly add a single-sentence soft closing text providing Kumaran's direct email (Kumaran.alchemist@gmail.com) and contact (+91 96000 57231) for scheduling an exploratory call.

Context Dossier:
{context}"""

# ==============================================================================
# 3. INTERFACE HEADER RENDERING
# ==============================================================================
st.title("💼 Kumaran Parvatham")
st.subheader("AI Executive Talent Agent")
st.write(
    "Welcome! I am Kumaran's autonomous career agent. You can ask me questions about his "
    "24+ years of experience across Banking, Fintech, Payments, Enterprise Transformation, "
    "or use the **Job Matcher** tool to evaluate his fit for your open role instantly."
)

if not os.getenv("OPENAI_API_KEY"):
    st.error("Missing OpenAI API Key! Please verify your Streamlit Cloud Secrets settings.")
    st.stop()

# Set repository fallback directory cleanly
DATA_DIR = "."
if os.path.exists("/mount/src/kumaran-career-agent/bio.md"):
    DATA_DIR = "/mount/src/kumaran-career-agent"

from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# ==============================================================================
# 4. EXPLICIT DOSSIER PARSING (NO LOOP SYNTAX RISKS)
# ==============================================================================
@st.cache_resource
def initialize_rag_pipeline(target_dir):
    all_loaded_docs = []
    
    bio_f = os.path.join(target_dir, "bio.md")
    if os.path.exists(bio_f):
        all_loaded_docs.extend(TextLoader(bio_f, encoding="utf-8").load())

    exp_f = os.path.join(target_dir, "experience.md")
    if os.path.exists(exp_f):
        all_loaded_docs.extend(TextLoader(exp_f, encoding="utf-8").load())

    proj_f = os.path.join(target_dir, "projects.md")
    if os.path.exists(proj_f):
        all_loaded_docs.extend(TextLoader(proj_f, encoding="utf-8").load())

    faq_f = os.path.join(target_dir, "faq.md")
    if os.path.exists(faq_f):
        all_loaded_docs.extend(TextLoader(faq_f, encoding="utf-8").load())

    if not all_loaded_docs:
        st.error("Dossier Assets Missing from Repository Root Context.")
        st.stop()

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(all_loaded_docs, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 4})

# Warm up parameters cleanly using the flattened framework loop
retriever = initialize_rag_pipeline(DATA_DIR)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0) # Temperature 0 forces strict text copy behavior

# Initialize Session State arrays safely outside block grids
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==============================================================================
# 5. FRONTEND WORKSPACE GRID DISPLAY
# ==============================================================================
col1, col2 = st.columns(2, gap="large")

# --- COLUMN 1: THE INTERACTIVE JOB MATCHER ---
with col1:
    st.markdown("### 🎯 Option A: Match Your Job Description")
    st.write("Paste your target JD below to get an instant, metric-backed gap analysis mapping Kumaran's career dossier directly to your requirements.")
    
    jd_input = st.text_area("Paste Job Description here:", height=300, key="jd_input_box", placeholder="Looking for a Product/Transformation Executive with experience...")
    
    if st.button("Analyze Role Fit ⚡️"):
        if jd_input.strip() == "":
            st.warning("Please paste a valid job description text.")
        else:
            with st.spinner("Executing structural alignment matrix..."):
                relevant_docs = retriever.invoke(jd_input)
                context_dossier = format_docs(relevant_docs)
                
                match_prompt = ChatPromptTemplate.from_messages([
                    ("system", SYSTEM_JOB_MATCHER_INSTRUCTION),
                    ("human", "Analyze this job description and produce the explicit scorecard framework output:\n{jd}")
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
    
    chat_container = st.container(height=400)
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
    recruiter_query = st.chat_input("Ask about portfolio scales, tech stacks, or availability...")
    
    if recruiter_query:
        # Append User Message and render instantly
        st.session_state.messages.append({"role": "user", "content": recruiter_query})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(recruiter_query)
        
        # Build prompt templates cleanly
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_CHAT_INSTRUCTION),
            ("human", "{input}")
        ])
        
