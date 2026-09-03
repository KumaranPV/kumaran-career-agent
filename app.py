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
Answer the user's question using the provided context dossier below.

CRITICAL CONVERSATIONAL DIRECTION:
- Maintain a polished, articulate, professional executive tone.
- Your dossier contains a structured 'High-Stakes Adversarial Vetting Dossier' with three distinct layers of information for key topics: 'Layer 1 — Quick Response', 'Layer 2 — Detailed Explanation', and 'Layer 3 — Show me the evidence'.

STRICT NARRATIVE EXSTRUCTION ROUTING MANDATES:
1. IF ASKED ABOUT GAPS ('What are Kumaran's biggest gaps for this role?'):
   Deliver this exact statement: 'Kumaran’s strongest experience sits at the intersection of payments, product/platform leadership and large-scale transformation. His potential gaps depend on the mandate. He should not be positioned as a career software-engineering leader, enterprise architect, or executive with long-term standalone P&L ownership. Similarly, where a role requires deep local-market knowledge, an existing work permit, or mandatory local-language fluency, these may be practical gaps rather than capability gaps. Where the requirement is adjacent rather than absent—for example engineering leadership, architecture decisions or commercial ownership—the distinction should be explored in interview rather than treated as a binary mismatch.'

2. IF ASKED ABOUT HANDLING, LEADING, OR MANAGING ENGINEERING TEAMS:
   You MUST explain his role as a matrix coordinator connecting definitions with execution nodes, rather than a line manager. By default, output this exact text verbatim:
   'Kumaran has extensive experience leading engineering execution in a matrix environment, but should not be described as a career Head of Engineering. He has worked closely with engineering teams across product roadmaps, prioritisation, architecture dependencies, release planning, defects, production stability, non-functional requirements, SRE, testing and operational readiness. At Zeta, he coordinated Product, Engineering, Architecture, Quality, Operations, SRE, Risk/InfoSec and customer delivery branches to scale capabilities safely.'

3. FOR GENERAL LAYER INTERACTION STRATEGY:
   - If the user asks for a simple quick response or basic question on other topics, deliver the text from 'Layer 1 — Quick Response' for that specific topic verbatim.
   - If the user explicitly asks for "details", "elaboration", "more depth", or an "explanation", deliver the text from 'Layer 2 — Detailed Explanation' for that topic verbatim.
   - If the user explicitly asks for "evidence", "metrics", "case studies", or "show me the evidence", deliver the complete text blocks from 'Layer 3 — Show me the evidence' for that specific topic verbatim.

*Formatting Rule: Do not print label prefixes like 'Layer 1' or 'Topic' to the screen. Simply present the core response text naturally and cleanly.*

At the end of your response, seamlessly add a single-sentence soft closing text providing Kumaran's direct email (Kumaran.alchemist@gmail.com) and contact (+91 96000 57231) for scheduling an exploratory call.

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
st.info("**🎯 Option A: Assess against my job description** - Use the Job Matcher layout directly below.")
st.info("**📈 Option B: Understand his track record & Challenge the profile** - Use the Chat Console terminal found further down the page.")

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
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1) 

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
