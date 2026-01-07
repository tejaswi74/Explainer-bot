import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API key from tour.env
load_dotenv("tour.env")

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("Google API Key not found in tour.env")
    st.stop()

# Configure Gemini
genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = """
You are a Travel Booking Process & Policy Explainer Bot.
You ONLY explain:
- Travel booking steps
- Cancellation processes
- Travel documentation requirements
- Common travel policies

You MUST NOT:
- Book tickets
- Cancel bookings
- Process payments
- Handle refunds

Explain clearly in simple language.
"""

@st.cache_resource
def get_model():
    return genai.GenerativeModel("gemini-flash-latest")

model = get_model()

@st.cache_data
def generate_response(question):
    try:
        response = model.generate_content(SYSTEM_PROMPT + "\n\nUser Question: " + question)
        text = getattr(response, "text", None) or (response[0].get("content") if isinstance(response, (list, tuple)) and response else None) or str(response)
        return text
    except Exception as gen_e:
        raise gen_e

st.set_page_config(page_title="Travel Policy Explainer Bot")
st.title("🧳 Travel Booking Process & Policy Explainer Bot")

# Sidebar with information
with st.sidebar:
    st.header("About this Bot")
    st.markdown("""
    This bot helps explain travel booking processes and policies. It can answer questions about:
    - Booking steps
    - Cancellation policies
    - Documentation requirements
    - Common travel policies
    
    **Note:** This bot only provides information and explanations. It cannot book tickets or process transactions.
    """)
    st.markdown("---")
    st.markdown("Powered by Google Gemini")

question = st.text_input("Ask a travel policy question:", placeholder="e.g., How do I cancel a flight booking?")

if st.button("Explain"):
    if question.strip():
        try:
            text = generate_response(question)
            st.write(text)
        except Exception as gen_e:
            error_str = str(gen_e).lower()
            if "quota" in error_str or "429" in error_str or "exceeded" in error_str:
                st.error("Quota exceeded for the Gemini API. You've reached the free tier limits.")
                st.info("To continue using the service:")
                st.markdown("- Wait for the quota to reset (typically daily)")
                st.markdown("- Upgrade to a paid plan at [Google AI Studio](https://makersuite.google.com/app/apikey)")
                st.markdown("- Enable billing for your Google Cloud project")
            else:
                st.error(f"Error generating content: {gen_e}")
                st.info("If the chosen model does not support `generate_content`, try a text/chat model such as 'models/text-bison-001' or use the ListModels output above to pick a supported model.")
    else:
        st.warning("Please enter a question")
