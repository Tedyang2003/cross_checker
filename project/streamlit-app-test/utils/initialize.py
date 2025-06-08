import streamlit as st

def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

