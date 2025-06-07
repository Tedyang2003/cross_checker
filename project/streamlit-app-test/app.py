import streamlit as st
import json
import openai
import os
import pandas as pd
from dotenv import load_dotenv
import pathlib

load_dotenv()
st.set_page_config(layout="wide")

# ------------------- SESSION STATE -------------------
if "view" not in st.session_state:
    st.session_state["view"] = "home"
if "article_id" not in st.session_state:
    st.session_state["article_id"] = None
if "invisible_id" not in st.session_state:
    st.session_state["invisible_id"] = 0


# ------------------- FUNCTIONS -------------------
def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

def go_home():
    st.session_state["view"] = "home"
    st.session_state["article_id"] = None
    st.session_state["invisible_id"] = 1

def go_to_article(article_id):
    st.session_state["view"] = "facts"
    st.session_state["article_id"] = article_id

def set_chunk_id(i):
    st.session_state["invisible_id"] = i

# ------------------- CSS -------------------
css_path = pathlib.Path("assets/main.css")
load_css(css_path)

# ------------------- Load OpenAI -------------------
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------- Load Article(s) -------------------
ARTICLE_DIR = "articles"
FACT_DIR = "facts"

article_file = "article.json"  # Replace with dynamic ID if needed
with open(article_file, "r") as f:
    article_data = json.load(f)

article_title = article_data["title"]
article_content = article_data["content"]

# ------------------- Load / Generate Facts -------------------
if not int(os.getenv("QUICK_TEST")):
    def split_into_chunks(text, chunk_size=40):
        words = text.split()
        return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

    @st.cache_data(show_spinner=False)
    def summarize_chunk(chunk):
        prompt = f"You are a summarization assistant. Return only the topic in 5 words or fewer:\n\n{chunk}"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=20
        )
        return response.choices[0].message.content.strip()

    @st.cache_data(show_spinner=False)
    def extract_facts_with_contradictions(chunk):
        prompt = """
        Extract 3 to 5 atomic facts from the following text.
        For each fact, create 1 to 5 fake contradictions.
        Return the result as a JSON list in this exact format:
        [{"fact": "...", "contradictions": ["...", "..."]}]
        Do not include explanation or formatting and backticks
        Text:
        """ + chunk
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        try:
            content = response.choices[0].message.content.strip()
            print(content)
            return json.loads(content)
        except Exception as e:
            return [{"fact": "Parsing failed", "contradictions": [str(e)]}]

    chunks = split_into_chunks(article_content)
    summaries = [summarize_chunk(chunk) for chunk in chunks]
    facts_by_chunk = [extract_facts_with_contradictions(chunk) for chunk in chunks]
    rows = []
    for i, (chunk_text, summary, facts) in enumerate(zip(chunks, summaries, facts_by_chunk)):
        chunk_label = f"Chunk {i+1}"
        for item in facts:
            rows.append({
                "Chunk": chunk_label,
                "Chunk Text": chunk_text,
                "Summary": summary,
                "Fact": item.get("fact", ""),
                "Contradictions": "\n".join(item.get("contradictions", []))
            })
    df = pd.DataFrame(rows)
    df.to_csv("test.csv", index=False)
else:
    df = pd.read_csv('test.csv')

chunks_df = df[['Chunk', 'Chunk Text']].drop_duplicates().reset_index(drop=True)

# ------------------- VIEW LOGIC -------------------
if st.session_state["view"] == "home":
    st.title("📰 Article Catalog")
    st.markdown("Click on an article to explore extracted facts.")
    # For now, only one article
    with st.container():
        st.markdown(f"### {article_title}")
        st.markdown(article_content[:200] + "...")
        st.button("View Facts", on_click=go_to_article, args=("article.json",))

elif st.session_state["view"] == "facts":
    with st.container(key='facts'):
        st.button("← Back", on_click=go_home, key='back_button')


        idx = st.session_state["invisible_id"]
        if idx != -1:
            chunk_row = chunks_df.iloc[idx]
            chunk_label = chunk_row["Chunk"]
            chunk_text = chunk_row["Chunk Text"]
            st.markdown(f"### **{chunk_label}**")
            with st.container(key="divider"):
                st.markdown("---")

            # Get facts for selected chunk
            fact_rows = df[df["Chunk"] == chunk_label]
            expanded = True
            for _, row in fact_rows.iterrows():
                fact = row["Fact"]
                contradictions = row["Contradictions"].split("\n") if isinstance(row["Contradictions"], str) else []

                with st.expander(fact, expanded=expanded):
                    for c in contradictions:
                        st.markdown(f"- *{c.strip()}*")
                expanded = False
        else:
            st.markdown("Click a chunk to see its facts.")


    # Sidebar content updates dynamically
    with st.sidebar:
        
        with st.container(key='chunk_sect'):
            idx = st.session_state["invisible_id"]
            st.markdown(f"## {article_data['title']}")
            for i, row in chunks_df.iterrows():
                label = row["Chunk Text"]
                if idx == i:
                    with st.container(key='highlight_text'):
                        st.button(label, key=f"chunk-{i}", on_click=set_chunk_id, args=(i,))
                else:
                    st.button(label, key=f"chunk-{i}", on_click=set_chunk_id, args=(i,))


# Main conten
