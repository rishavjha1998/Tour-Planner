# app.py
import streamlit as st
from main import handle_user_query

st.title("🧳 AI Event Planner (CrewAI + Streamlit)")

user_query = st.text_area("Describe your trip or event:")

if st.button("Plan My Trip"):
    with st.spinner("Planning your event..."):
        result = handle_user_query(user_query)
        st.success("Here’s your trip plan:")
        st.write(result)