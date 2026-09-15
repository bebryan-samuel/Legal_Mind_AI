import streamlit as st
import project


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="LegalMind AI",
    page_icon="⚖️",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #0e1117;
}

.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

.hero {
    padding: 30px;
    border-radius: 18px;
    background: linear-gradient(
        135deg,
        #161b22,
        #202733
    );
    border: 1px solid #30363d;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 42px;
    margin-bottom: 5px;
}

.hero p {
    color: #aab2bf;
    font-size: 17px;
}

.answer-box {
    padding: 25px;
    border-radius: 15px;
    background-color: #161b22;
    border: 1px solid #30363d;
    margin-top: 20px;
}

.source-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #161b22;
    border: 1px solid #30363d;
    margin-bottom: 10px;
}

.badge {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 20px;
    background-color: #238636;
    color: white;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero">

<h1>⚖️ LegalMind AI</h1>

<p>
AI-powered Constitutional Research Assistant
</p>

<span class="badge">
🇮🇳 Constitution of India
</span>

</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ System")

    st.success("🟢 Hugging Face API Connected")

    st.success("🟢 FAISS Vector Search")

    st.success("🟢 BM25 Keyword Search")

    st.success("🟢 Constitution Loaded")

    st.divider()

    st.subheader("🤖 Model")

    st.write("Qwen3-8B")

    st.subheader("📚 Knowledge Base")

    st.write("Constitution of India")

    st.divider()

    st.caption(
        "⚠️ This system is for legal research and "
        "educational purposes. It is not a substitute "
        "for professional legal advice."
    )


# ============================================================
# QUESTION
# ============================================================

st.subheader("🔎 Ask a Constitutional Question")

question = st.text_area(
    "Enter your question",
    placeholder=(
        "Example: What does Article 21 guarantee?"
    ),
    height=100
)


# ============================================================
# EXAMPLE QUESTIONS
# ============================================================

st.write("**Try an example:**")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Article 21", use_container_width=True):
        question = "What does Article 21 guarantee?"

with col2:
    if st.button("Article 14", use_container_width=True):
        question = "What does Article 14 provide?"

with col3:
    if st.button("Citizenship", use_container_width=True):
        question = (
            "What are the constitutional provisions "
            "regarding citizenship?"
        )


# ============================================================
# SEARCH BUTTON
# ============================================================

if st.button(
    "🔍 Search Constitution",
    type="primary",
    use_container_width=True
):

    if not question.strip():

        st.warning(
            "Please enter a constitutional question."
        )

    else:

        with st.spinner(
            "Searching the Constitution and generating answer..."
        ):

            try:

                response, results = project.ask_question(
                    question
                )

                # Save results
                st.session_state["response"] = response
                st.session_state["results"] = results
                st.session_state["question"] = question

            except Exception as e:

                st.error(
                    f"Something went wrong: {str(e)}"
                )


# ============================================================
# DISPLAY ANSWER
# ============================================================

if "response" in st.session_state:

    st.divider()

    st.subheader("🤖 AI Answer")

    st.markdown(
        f"""
        <div class="answer-box">

        {st.session_state["response"]}

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # SOURCES
    # ========================================================

    st.subheader("📚 Constitution Sources")

    results = st.session_state["results"]

    for i, doc in enumerate(results, start=1):

        page = doc.metadata.get(
            "page",
            "Unknown"
        )

        if isinstance(page, int):
            page += 1

        with st.expander(
            f"📄 Source {i} — Constitution of India — Page {page}"
        ):

            st.write(
                doc.page_content
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "LegalMind AI • RAG + FAISS + BM25 + "
    "Hugging Face Qwen3-8B"
)