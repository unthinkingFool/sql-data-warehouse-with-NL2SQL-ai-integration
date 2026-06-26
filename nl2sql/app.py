
# nl2sql/app.py
"""
Streamlit UI for the NL2SQL warehouse query interface.
Run with: streamlit run nl2sql/app.py
"""

import sys
from pathlib import Path

# Add parent folder to path so "nl2sql" can be imported as a package
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from nl2sql.pipeline import run_pipeline
from nl2sql.embedder import build_index

# --- Page config ---
st.set_page_config(
    page_title="Warehouse Query Assistant",
    page_icon="📊",
    layout="wide"
)

# --- Initialize RAG index (once per session) ---
@st.cache_resource(show_spinner="Building schema index...")
def load_index():
    return build_index()

load_index()

# --- Header ---
st.title("📊 Warehouse Query Assistant")
st.caption(
    "Ask any business question in plain English. "
    "The system uses RAG to retrieve schema context, then Llama 3.3 (via Groq) to generate SQL, "
    "then executes it against the Gold layer."
)

# --- Sidebar: Example questions ---
with st.sidebar:
    st.header("Example Questions")
    examples = [
        "Who are the top 10 customers by total revenue?",
        "What is the total revenue by product category?",
        "Show monthly sales trends for 2013",
        "Which country has the most VIP customers?",
        "What are the top 5 most expensive products in Bikes?",
        "What is the average order value by customer segment?",
        "How many orders were placed each year?",
        "Which products have never been sold?",
    ]
    st.caption("Click any question to run it:")
    for example in examples:
        if st.button(example, use_container_width=True, key=example):
            st.session_state["question_input"] = example

    st.divider()
    st.caption("**Architecture**")
    st.caption("1. User question → Embedding")
    st.caption("2. ChromaDB → Top-4 schema chunks")
    st.caption("3. Schema + question → Llama 3.3 (Groq) → SQL")
    st.caption("4. SQL → SQL Server Gold layer")
    st.caption("5. Results → Streamlit table")

# --- Main query interface ---
question = st.text_area(
    "Ask a question about the sales data:",
    value=st.session_state.get("question_input", ""),
    height=80,
    placeholder="e.g. What are the top 5 products by revenue in 2013?"
)

run_btn = st.button("Run Query", type="primary", use_container_width=False)

if run_btn and question.strip():
    with st.spinner("Running pipeline (RAG → Groq → SQL Server)..."):
        result = run_pipeline(question.strip())

    # --- Results ---
    if result.success and result.data is not None:
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Rows Returned", result.row_count)
        col2.metric("Execution Time", f"{result.execution_time_ms:.0f}ms")
        col3.metric("Confidence", result.confidence.capitalize())
        col4.metric("Schema Chunks Used", 4)

        # Data table
        st.subheader("📋 Results")
        st.dataframe(result.data, use_container_width=True, hide_index=True)

        # Download button
        csv = result.data.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "query_results.csv", "text/csv")

    else:
        st.error(f"Query failed: {result.error}")

    # --- Explanation ---
    st.subheader("💡 Explanation")
    st.write(result.explanation)

    if result.assumptions:
        st.caption("**Assumptions made:**")
        for a in result.assumptions:
            st.caption(f"- {a}")

    # --- Generated SQL ---
    with st.expander("🔍 View Generated SQL", expanded=False):
        st.code(result.generated_sql, language="sql")

    # --- Retrieved Schema Context ---
    with st.expander("📚 Schema Context Retrieved by RAG", expanded=False):
        st.text(result.retrieved_context)

elif run_btn:
    st.warning("Please enter a question first.")

# --- Footer ---
st.divider()
st.caption(
    "Built on top of a Medallion Architecture data warehouse "
    "(Bronze → Silver → Gold). "
    "RAG powered by ChromaDB + Sentence Transformers. "
    "SQL generation by Llama 3.3 70B Versatile (via Groq)."
)