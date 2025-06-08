from nltk import sent_tokenize
import streamlit as st
import json
import openai
import os
from dotenv import load_dotenv

load_dotenv()

# ------------------- Load OpenAI -------------------
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@st.cache_data(show_spinner=False)
def split_into_chunks(text, max_words=60):
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_len = 0

    for sentence in sentences:
        word_count = len(sentence.split())
        if current_len + word_count <= max_words:
            current_chunk.append(sentence)
            current_len += word_count
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_len = word_count

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

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