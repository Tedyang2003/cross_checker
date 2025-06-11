import streamlit as st
import time
from utils.navigate import go_to_facts
from utils.cross_check import split_into_chunks, summarize_chunk, extract_facts_with_contradictions
import pandas as pd
import numpy as np

def loading_page():
    st.header("Fact Checking in Progress")
    st.markdown("Please wait while we process your request")
    with st.sidebar:
        st.empty()  # immediately wipes the sidebar on all non-home views

    # Initialize state
    if "stage" not in st.session_state:
        st.session_state.stage = 1
    if "error" not in st.session_state:
        st.session_state.error = None

    article = st.session_state.article
    article_content = article['content'] 
    def reset():
        st.session_state.stage = 1
        st.session_state.error = None

    # Step 1: Get token
    if st.session_state.stage == 1:
        with st.spinner("Chunking Text ..."):
            time.sleep(2)
            try:
                # Simulate token retrieval
                max_words = 60
                chunks = split_into_chunks(article_content, max_words)
                with st.sidebar:
                    with st.container(key='details'):
                        st.markdown("# :violet[RAG System Details]")

                        with st.container(key="embedding_model"):
                            st.markdown(f"### Embeddings Model: &nbsp; all-mpnet-base-v2")

                        l, m, r = st.columns([1, 1, 1])
                        with l: 
                            st.metric(label="Chunks in article", value=f"{len(chunks)}")
                        with m:
                            st.metric(label="Similar chunks", value=10)
                        with r:
                            st.metric(label="Number of articles", value=7)
                st.success("Text successfully chunked")
                st.session_state.stage = 2
            except Exception as e:
                st.session_state.error = f"Step 1 failed: {str(e)}"

    # Step 2: Fetch data
    if st.session_state.stage == 2 and not st.session_state.error:
        with st.spinner("Step 2: Summarizing chunks..."):
            time.sleep(2)
            try:
                # Simulate API call
                summaries = [summarize_chunk(chunk) for chunk in chunks]
                st.success("Chunks summarized.")
                st.session_state.stage = 3
            except Exception as e:
                st.session_state.error = f"Step 2 failed: {str(e)}"

    # Step 3: Submit response
    if st.session_state.stage == 3 and not st.session_state.error:
        with st.spinner("Step 3: Extracting facts and cross checking..."):
            time.sleep(2)
            try:    
                facts_by_chunk = [extract_facts_with_contradictions(chunk) for chunk in chunks]
                # Simulate successful submission
                st.success("Facts Extracted and Cross Referenced.")
                st.session_state.stage = 4
            except Exception as e:
                st.session_state.error = f"Step 3 failed: {str(e)}"

    # Handle error
    if st.session_state.error:
        st.error(st.session_state.error)
        col1, col2 = st.columns(2)
        with col1:
            st.button("Retry", on_click=reset)
        with col2:
            st.button("Back", on_click=lambda: st.session_state.update(view="home", stage=1, error=None))
        return

    # Final screen
    if st.session_state.stage == 4:
        st.success("All steps completed successfully.")
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
        summary_df = (
            df.groupby(["Summary"], as_index=False)
            .agg({
                "Fact": "count",
            })
            .rename(columns={
                "Fact": "Facts Total",
            })
        )

        # Add fake Contra/Sim Ratio column with random values between 0.1 and 2.0
        # Generate fake ratio
        summary_df["Contra/Sim"] = np.round(np.random.uniform(0.1, 2.0, size=len(summary_df)), 2)

        threshold = 1.0  # Set threshold

        def style_contra_sim(val):
            try:
                val = float(val)
                if val > threshold:
                    return "color:  #99ff99"  # green
                elif val < threshold:
                    return "color:  #ff9999"  # red
                else:
                    return ""
            except:
                return ""

        # Apply text color styling only to Contra/Sim column
        styled_df = summary_df.style.applymap(style_contra_sim, subset=["Contra/Sim"]).format({"Contra/Sim": "{:.2f}"})  # force 2 decimal places in display

        with st.sidebar:
            st.markdown("")
            st.markdown("# :violet[Factual Summary]")
            st.markdown("")
            st.dataframe(styled_df, hide_index=True)
        st.session_state.processed_facts = df
        st.markdown("")
        st.markdown("")
        st.button("Proceed to View Facts", on_click=go_to_facts)
        chunks_df = df[['Chunk', 'Chunk Text']].drop_duplicates().reset_index(drop=True)
        st.session_state.chunks_df = chunks_df
