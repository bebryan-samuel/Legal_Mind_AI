from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

load_dotenv()

print("Loading Constitution of India PDF...")

loader = PyPDFLoader("coi/constitution_of_india.pdf")
documents = loader.load()


# ============================================================
# 1. CHECK HUGGING FACE TOKEN
# ============================================================

HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

if not HF_TOKEN:
    raise ValueError(
        "HF_TOKEN not found. Add your Hugging Face token to .env"
    )

os.environ["HF_TOKEN"] = HF_TOKEN

# ============================================================
# 2. PDF LOADER
# ============================================================



# ============================================================
# 3. TEXT SPLITTER
# ============================================================

print("Splitting document into chunks...")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1100,
    chunk_overlap=200,
    separators=[
        "\nPART ",
        "\nCHAPTER ",
        "\n\n",
        "\n",
        "। ",
        ". ",
        " ",
        ""
    ]
)

chunks = splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks")


# ============================================================
# 4. EMBEDDINGS
# ============================================================

print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# ============================================================
# 5. VECTOR STORE
# ============================================================

print("Creating FAISS vector database...")

vectorstore = FAISS.from_documents(
    chunks,
    embeddings
)
print("Creating hybrid retriever...")

# FAISS semantic retriever
faiss_retriever = vectorstore.as_retriever(
    search_kwargs={"k": 8}
)

# BM25 keyword retriever
bm25_retriever = BM25Retriever.from_documents(
    chunks,
    k=8
)

print("Hybrid retriever ready")


# ============================================================
# 6. HUGGING FACE INFERENCE API
# ============================================================

print("Connecting to Hugging Face Inference API...")

client = InferenceClient(
    api_key=HF_TOKEN,
    provider="auto"
)

print("Hugging Face LLM ready")


# ============================================================
# 7. USER QUESTION
# ============================================================

question = input("\nAsk your question: ")




# ============================================================
# 8. HYBRID RETRIEVAL
# ============================================================

print("\nSearching Constitution...")

# Semantic search
faiss_results = faiss_retriever.invoke(question)

# Exact/keyword search
bm25_results = bm25_retriever.invoke(question)

# ------------------------------------------------------------
# Combine results
# ------------------------------------------------------------

combined = []

seen = set()

for doc in bm25_results + faiss_results:
    content = doc.page_content.strip()

    if content not in seen:
        combined.append(doc)
        seen.add(content)

# ------------------------------------------------------------
# LEGAL REFERENCE DETECTION
# ------------------------------------------------------------

import re

exact_matches = []

# ============================================================
# A. ARTICLE NUMBER QUERY
# ============================================================

article_match = re.search(
    r"\barticle\s+(\d+[A-Za-z]?)\b",
    question,
    re.IGNORECASE
)

if article_match:

    article_number = article_match.group(1)

    print(f"Detected Article: {article_number}")

    article_pattern = re.compile(
        rf"(?:"
        rf"\bArticle\s+{re.escape(article_number)}\b"
        rf"|"
        rf"^{re.escape(article_number)}[\.\s]"
        rf")",
        re.IGNORECASE | re.MULTILINE
    )

    exact_matches = [
        doc
        for doc in chunks
        if article_pattern.search(doc.page_content)
    ]


# ============================================================
# B. CITIZENSHIP QUERY
# ============================================================

if "citizenship" in question.lower() or "citizen" in question.lower():

    print("Detected citizenship query")

    citizenship_keywords = [
        "citizenship",
        "citizen",
        "citizens",
        "Article 5",
        "Article 6",
        "Article 7",
        "Article 8",
        "Article 9",
        "Article 10",
        "Article 11"
    ]

    citizenship_matches = []

    for doc in chunks:

        text = doc.page_content.lower()

        score = 0

        for keyword in citizenship_keywords:

            if keyword.lower() in text:
                score += 1

        if score > 0:

            citizenship_matches.append(
                (score, doc)
            )

    # Highest keyword score first
    citizenship_matches.sort(
        key=lambda x: x[0],
        reverse=True
    )

    citizenship_docs = [
        doc
        for score, doc in citizenship_matches
    ]

    exact_matches = citizenship_docs + exact_matches


# ============================================================
# PUT LEGAL MATCHES FIRST
# ============================================================

combined = exact_matches + combined


# ============================================================
# REMOVE DUPLICATES
# ============================================================

final_results = []
seen = set()

for doc in combined:

    content = doc.page_content.strip()

    if content not in seen:
        final_results.append(doc)
        seen.add(content)


# ============================================================
# SELECT TOP RESULTS
# ============================================================

results = final_results[:5]

print(f"Retrieved {len(results)} relevant chunks")


# ============================================================
# BUILD CONTEXT
# ============================================================

context = "\n\n".join(
    doc.page_content
    for doc in results
)


# ============================================================
# SHOW RETRIEVED CONTEXT
# ============================================================

print("\n========== RETRIEVED CONTEXT ==========\n")

for i, doc in enumerate(results, start=1):

    page = doc.metadata.get("page", "Unknown")

    print(f"--- Source {i} | Page {page} ---")
    print(doc.page_content[:800])
    print()


# ============================================================
# 9. LEGAL PROMPT
# ============================================================

prompt = f"""
You are a legal research assistant specializing in the Constitution of India.

Answer ONLY using the provided Constitution context.

Do not invent Articles, provisions, cases, or facts.

If the answer is not available in the context, say:

"I could not find sufficient information in the provided Constitution."

Context:
{context}

Question:
{question}

Give the answer in this format:

Relevant Article/Provision:

Explanation:

Answer:
"""


# ============================================================
# 10. GENERATE ANSWER USING HUGGING FACE API
# ============================================================

print("\nGenerating answer using Hugging Face Inference API...")

completion = client.chat.completions.create(
    model="Qwen/Qwen3-8B",
    messages=[
        {
            "role": "system",
            "content": "You are a legal research assistant specializing in the Constitution of India. Answer only using the provided context."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    max_tokens=300,
    temperature=0.2
)

response = completion.choices[0].message.content


# ============================================================
# 11. DISPLAY ANSWER
# ============================================================

print("\n========== AI ANSWER ==========\n")

print(response)

print("\n========== SOURCES ==========\n")

for i, doc in enumerate(results, start=1):
    page_number = doc.metadata.get("page", "Unknown")

    print(
        f"Source {i}: Constitution of India - "
        f"Page {page_number + 1 if isinstance(page_number, int) else page_number}"
    )
