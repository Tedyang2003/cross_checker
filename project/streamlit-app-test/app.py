import streamlit as st
import json
import pathlib
import nltk
from utils.reload import reload_modules
reload_modules()

# Then import after reload
from utils.initialize import load_css
from pages.home import home_page
from pages.load import loading_page
from pages.fact import fact_page


nltk.download('punkt_tab')
st.set_page_config(layout="wide")

# ------------------- SESSION STATE -------------------
if "view" not in st.session_state:
    st.session_state["view"] = "home"
if "article_id" not in st.session_state:
    st.session_state["article_id"] = None
if "invisible_id" not in st.session_state:
    st.session_state["invisible_id"] = 0

if "sidebar" not in st.session_state:
    st.session_state['sidebar'] = False


# ------------------- CSS -------------------
css_path = pathlib.Path("assets/main.css")
load_css(css_path)

ARTICLE_FILE = "articles.json"  # This should contain a JSON array of articles
with open(ARTICLE_FILE, "r") as f:
    all_articles = json.load(f)["articles"]

# ------------------- PAGE ROUTER -------------------
if st.session_state["view"] == "home":
    with st.sidebar:
        st.empty()  # immediately wipes the sidebar on all non-home views
    home_page(all_articles)

elif st.session_state["view"] == "loading_facts":
    with st.sidebar:
        st.empty()  # immediately wipes the sidebar on all non-home views
    loading_page()
    

elif st.session_state["view"] == "facts":
    with st.sidebar:
        st.empty()  # immediately wipes the sidebar on all non-home views
    fact_page()

# Main conten
