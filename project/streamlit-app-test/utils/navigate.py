import streamlit as st

def go_home():
    st.session_state["view"] = "home"
    st.session_state["article_id"] = None
    st.session_state["invisible_id"] = 0
    st.session_state.sidebar = False


def go_to_facts():
    st.session_state["view"] = "facts"
    st.session_state["article_id"] = None
    st.session_state["invisible_id"] = 0
    st.session_state.sidebar = False

    if "stage" in st.session_state:
        st.session_state.stage = 1

def go_to_article(article_id, article):
    st.session_state["view"] = "loading_facts"
    st.session_state["article_id"] = article_id
    st.session_state['article'] = article
    st.session_state.sidebar = True



def set_chunk_id(i):
    st.session_state["invisible_id"] = i