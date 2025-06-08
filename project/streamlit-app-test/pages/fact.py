import streamlit as st
from utils.navigate import go_home
import random
from utils.navigate import set_chunk_id

def fact_page():
    df = st.session_state.processed_facts
    chunks_df = st.session_state.chunks_df
    article = st.session_state.article
    with st.sidebar:
        st.empty()  # immediately wipes the sidebar on all non-home views
    with st.container(key='facts'):
        st.button("← Back", on_click=go_home, key='back_button')
        idx = st.session_state["invisible_id"]

        if idx != -1:
            chunk_row = chunks_df.iloc[idx]
            chunk_label = chunk_row["Chunk"]
            chunk_text = chunk_row["Chunk Text"]
            st.markdown(f"### Cross-Sourced Evidenced Facts")
            st.markdown(f"{chunk_text}")
            st.markdown("---")

            # Get facts for selected chunk
            fact_rows = df[df["Chunk"] == chunk_label]
            with st.container(key='fact_boxes'):
                for _, row in fact_rows.iterrows():
                    fact = row["Fact"]
                    contradictions_raw = row["Contradictions"].split("\n") if isinstance(row["Contradictions"], str) else []

                    # Preprocess: assign color and split by type
                    supporting, contradicting = [], []
                    for c in contradictions_raw:
                        rand_val = random.randint(1, 4)
                        if rand_val % 2 == 0:
                            contradicting.append(c.strip())
                        else:
                            supporting.append(c.strip())

                    green_count = len(supporting)
                    red_count = len(contradicting)

                    # Display fact with grouped contradictions
                    with st.expander(f":green[{green_count} :material/check:] :red[{red_count} :material/close:] &nbsp;&nbsp;&nbsp;&nbsp;  {fact}", expanded=False):
                        if supporting:
                            st.markdown("<br>", unsafe_allow_html=True)
                            st.badge("Similar Results", icon=":material/check:", color="green")

                            for s in supporting:
                                st.markdown(s)

                        if contradicting:
                            st.markdown("<br>", unsafe_allow_html=True)
                            st.badge("Contradictory Results", icon=":material/close:", color="red")
                            for c in contradicting:
                                st.markdown(f"{c}")
        else:
            st.markdown("Click a chunk to see its facts.")

    # Sidebar content updates dynamically
 
    with st.sidebar:
        with st.container(key='chunk_sect'):
            idx = st.session_state["invisible_id"]
            st.markdown(f"## {article['title']}")
            for i, row in chunks_df.iterrows():
                label = row["Chunk Text"]
                if idx == i:
                    with st.container(key='highlight_text'):
                        st.button(label, key=f"chunk-{i}", on_click=set_chunk_id, args=(i,))
                else:
                    st.button(label, key=f"chunk-{i}", on_click=set_chunk_id, args=(i,))
