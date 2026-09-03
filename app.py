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
You must follow the instructions inside 'scoring_rules.md' and 'system_rules.md' precisely.
Calculate and output an exact structured scorecard mapping perfectly to his evidence.

Context Dossier:
{context}"""

SYSTEM_CHAT_INSTRUCTION = """You are the autonomous, professional Executive Talent Agent for Kumaran Parvatham.
Answer the user's question using the provided context dossier below.

CRITICAL INSTRUCTIONS:
- You must strictly obey all principles, behavioral constraints, and response modes laid out inside 'system_rules.md' at all times.
- Position Kumaran based on his exact ownership levels, and adhere to approved/prohibited wordings provided in the context.
- End every substantive answer with: **Evidence used:** followed by the specific record IDs or source sections.

Context Dossier:
{context}"""

# ==============================================================================
# 3. INTERFACE HEADER RENDERING (PREMIUM RECRUITER EXPERIENCE)
# ==============================================================================
st.markdown("## 🔍 Should Kumaran be on your shortlist?")
st.write(
    "I am an AI career dossier built specifically to help hiring managers, executive search panels, "
    "and talent partners evaluate **Kumaran Parvatham** instantly against your specific leadership mandate."
)

st.markdown("### 🛠️ Use this ecosystem to:")
c1, c2, c3 = st.columns(3)
with c1:
    st.info("**🎯 Option A: Assess against my job description**\n\nPaste your target JD in *Option A* below to generate a metric-backed fit scorecard.")
with c2:
    st.info("**📈 Option B: Understand his track record**\n\nUse *Option B* to explore payments, product, transformation, AI frameworks, or commercial outcomes.")
with c3:
    st.info("**⚡ Challenge the profile**\n\nUse *Option B* to stress-test his explicit gaps, organizational limits, and interview focus points.")

st.markdown("<p style='text-align: center; font-weight: bold; color: #888;'>Or ask your own question below in the Option B terminal box.</p>", unsafe_allow_html=True)

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
# 4. EXPLICIT DOSSIER PARSING (FULLY SEVEN-FILE INTEGRATED V2 PIPELINE)
# ==============================================================================
@st.cache_resource
def initialize_rag_pipeline(target_dir):
    all_loaded_docs = []
    
    # 1. Base Profiles
    if os.path.exists(os.path.join(target_dir, "bio.md")):
        all_loaded_docs.extend(TextLoader(os.path.join(target_dir, "bio.md"), encoding="utf-8").load())
    if os.path.exists(os.path.join(target_dir, "experience.md")):
        all_loaded_docs.extend(TextLoader(os.path.join(target_dir, "experience.md"), encoding="utf-8").load())
    if os.path.exists(os.path.join(target_dir, "projects.md")):
        all_loaded_docs.extend(TextLoader(os.path.join(target_dir, "projects.md"), encoding="utf-8").load())
    if os.path.exists(os.path.join(target_dir, "faq.md")):
        all_loaded_docs.extend(TextLoader(os.path.join(target_dir, "faq.md"), encoding="utf-8").load())
        
    # 2. V2 Strict System Rules & Scoring Data
    if os.path.exists(os.path.join(target_dir, "system_rules.md")):
        all_loaded_docs.extend(TextLoader(os.path.join(target_dir, "system_rules.md"), encoding="utf-8").load())
    if os.path.exists(os.path.join(target_dir, "scoring_rules.md")):
        all_loaded_docs.extend(TextLoader(os.path.join(target_dir, "scoring_rules.md"), encoding="utf-8").load())
        
    # 3. Stable Evidence Ledger Configuration File
    if os.path.exists(os.path.join(target_dir, "evidence_ledger.yaml")):
        all_loaded_docs.extend(TextLoader(os.path.join(target_dir, "evidence_ledger.yaml"), encoding="utf-8").load())

    if not all_loaded_docs:
        st.error("Dossier Assets Missing from Repository Root Context.")
        st.stop()

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(all_loaded_docs, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 6}) # k=6 ensures rules and ledger load into context window cleanly

# Warm up parameters cleanly using the flattened framework loop
retriever = initialize_rag_pipeline(DATA_DIR)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0) # Temperature 0 forces exact replication without rewriting

# Initialize Session State arrays safely outside block grids
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome. I am Kumaran's executive talent agent. Ask me any question about his track record, leadership philosophy, domain gaps, or reasons to hire."}
    ]

# ==============================================================================
# 5. LINEAR WORKSPACE LAYOUT (ZERO NESTING TO GUARANTEE LIFTOFF)
# ==============================================================================
st.markdown("---")

# --- SECTION 1: THE INTERACTIVE JOB MATCHER (OPTION A) ---
st.markdown("### 🎯 Option A: Match Your Job Description")
st.write("Paste your target JD below to get an instant, metric-backed gap analysis scorecard mapping Kumaran's career dossier directly to your requirements.")

jd_input = st.text_area("Paste Job Description here:", height=200, key="jd_input_box_flat_final", placeholder="Looking for a Product/Transformation Executive with experience in banking core systems, scaling platforms, card-management system migrations...")

execute_match = st.button("Analyze Role Fit ⚡️")

if execute_match and jd_input.strip() != "":
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

st.markdown("---")

# --- SECTION 2: THE 24/7 CHAT CONSOLE (OPTION B) ---
st.markdown("### 💬 Option B: General Recruiter Q&A Console")
st.write("Ask specific exploratory or adversarial questions about Kumaran's leadership competencies, technical tools, or project frameworks.")

chat_container = st.container(height=350)

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

recruiter_query = st.chat_input("Ask about portfolio scales, tech stacks, or availability...")

if recruiter_query:
    st.session_state.messages.append({"role": "user", "content": recruiter_query})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(recruiter_query)
    
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_CHAT_INSTRUCTION),
        ("human", "{input}")
    ])
    context_docs = format_docs(retriever.invoke(recruiter_query))
    chat_chain = chat_prompt | llm | StrOutputParser()
    answer = chat_chain.invoke({"context": context_docs, "input": recruiter_query})
    
    with chat_container:
        with st.chat_message("assistant"):
            st.markdown(answer)
            
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
