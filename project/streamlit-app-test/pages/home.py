import streamlit as st
from utils.navigate import go_to_article
import datetime

def home_page(all_articles):
    with st.sidebar:
        st.empty()  # immediately wipes the sidebar on all non-home views
    l, main, r = st.columns([1, 6, 1])
    with main:
        st.title("Articles")
        st.markdown("Click on an article to explore extracted facts.")
        # For now, only one article
        # ------------------- DISPLAY ARTICLES -------------------
        with st.container(key="articles"):
            for idx, article in enumerate(all_articles):
                with st.container(border=True):
                    st.markdown(f"### {article['title']}")
                    st.markdown(article["content"][:200] + "...")
                    st.button("Cross Check", on_click=go_to_article, args=(idx, article), key=f"view_facts_{idx}")

    # --- Sidebar Filter UI ---
    with st.sidebar:
        with st.container(key='filter_sect'):

            st.markdown("# Filter Articles later")
            
            # Search title
            title = st.text_input("Search by Title", key="filter_title", placeholder="Enter a title ...")

            # Category filter
            category = st.selectbox(
                "Category",
                options=["All", "Disaster", "Environment", "Politics", "Health"],
                key="filter_category"
            )

            # Calendar date picker
            selected_date = st.date_input(
                "Select Date",
                value= datetime.date(2019, 7, 6),
                key="filter_date",
            )

            st.divider()

            # Filter action
            st.button("Apply Filters", key="apply_filters")