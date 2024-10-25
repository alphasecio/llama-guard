import os, streamlit as st
from groq import Groq

# Define a dictionary to map against MLCommons taxonomy of hazards
category_mapping = {
    "S1": "Violent Crimes",
    "S2": "Non-Violent Crimes",
    "S3": "Sex-Related Crimes",
    "S4": "Child Sexual Exploitation",
    "S5": "Defamation",
    "S6": "Specialized Advice",
    "S7": "Privacy",
    "S8": "Intellectual Property",
    "S9": "Indiscriminate Weapons",
    "S10": "Hate",
    "S11": "Suicide & Self-Harm",
    "S12": "Sexual Content",
    "S13": "Elections",
    "S14": "Code Interpreter Abuse"
}

# Function to handle Llama Guard response
def parse_response(response):
    # Split the response into the verdict and the categories (if any)
    parts = response.split()

    if len(parts) == 0:
        return "Invalid response", None

    verdict = parts[0].capitalize()  # Safe or Unsafe

    # Extract categories if the verdict is Unsafe
    categories = []
    if verdict == "Unsafe" and len(parts) > 1:
        violations = parts[1].split("/")
        categories = [category_mapping.get(violation, violation) for violation in violations]
    
    return verdict, categories

# Streamlit app
st.subheader("Llama Guard")
with st.sidebar:
  groq_api_key = st.text_input("Groq API Key", type="password")

col1, col2 = st.columns([4,1])  
prompt = col1.text_input("Prompt", label_visibility="collapsed")
validate = col2.button("Validate")

# If the Validate button is clicked
if validate:
  if not groq_api_key.strip() or not prompt.strip():
    st.error("Please provide the missing fields.")
  else:
    try:
      # Initialize Groq client after validating API key
      client = Groq(api_key=groq_api_key)
      
      with st.spinner("Please wait..."):
        # Run llama-guard-3-8b content moderation model on Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-guard-3-8b",
        )

        # Parse response and display results
        verdict, categories = parse_response(chat_completion.choices[0].message.content)

        st.markdown(f"**Verdict**: {verdict}")
        if verdict == "Unsafe" and categories:
          st.markdown("**Categories Violated**:")
          st.markdown("<ul>", unsafe_allow_html=True)
          for category in categories:
              st.markdown(f"<li>{category}</li>", unsafe_allow_html=True)
          st.markdown("</ul>", unsafe_allow_html=True)
    except Exception as e:
      st.exception(f"Exception: {e}")
