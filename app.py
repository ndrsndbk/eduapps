
import streamlit as st

st.set_page_config(page_title="Neuro Niche - Test App", page_icon="🧠")

st.title("🧠 Neuro Niche - Test Streamlit App")
st.write("This is a lightweight test version to confirm Streamlit deployment.")

name = st.text_input("Enter your name")
if st.button("Submit"):
    st.success(f"Welcome, {name}!")
