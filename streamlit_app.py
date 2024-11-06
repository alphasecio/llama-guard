import os, streamlit as st
from groq import Groq

# Define a dictionary to map against MLCommons taxonomy of hazards
SAFETY_CATEGORIES = {
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
    # Split the response into lines and clean up
    response = response.strip()
    
    if response.lower().startswith("safe"):
        return "Safe", None
        
    # For unsafe responses, look for category codes
    categories = []
    # Look for any S1-S14 patterns in the response
    for category_code in SAFETY_CATEGORIES.keys():
        if category_code in response:
            categories.append(f"{category_code}: {SAFETY_CATEGORIES[category_code]}")
    
    return "Unsafe", categories

# Streamlit app config
st.set_page_config(
    page_title="Llama Guard Safety Checker",
    page_icon="🛡️",
    initial_sidebar_state="auto",
)

st.subheader("Llama Guard Safety Checker")
with st.sidebar:
  st.markdown(
    """
    [Llama Guard](https://www.llama.com/docs/model-cards-and-prompt-formats/llama-guard-3) is an LLM-based input-output safeguard model geared towards Human-AI conversation use cases.
    
    If the input is determined to be safe, the response will be `Safe`. Else, the response will be `Unsafe`, followed by one or more of the violating categories:
    * S1: Violent Crimes. 
    * S2: Non-Violent Crimes. 
    * S3: Sex Crimes. 
    * S4: Child Sexual Exploitation. 
    * S5: Defamation. 
    * S6: Specialized Advice. 
    * S7: Privacy. 
    * S8: Intellectual Property. 
    * S9: Indiscriminate Weapons. 
    * S10: Hate. 
    * S11: Suicide & Self-Harm. 
    * S12: Sexual Content. 
    * S13: Elections.
    * S14: Code Interpreter Abuse. 
    """
  )
  groq_api_key = st.text_input("Groq API Key", type="password", help="Get your API key [here](https://console.groq.com/keys).")

prompt = st.text_area("Enter your prompt here", height=200)
analyse = st.button("Analyse")

# If the Analyse button is clicked
if analyse:
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

        if verdict == "Safe":
          st.success("✅ Safe: This content appears to be safe for AI interactions.")
        else:
          st.error("❌ Unsafe: This content may not be appropriate for AI interactions.")
          if categories:
            st.markdown("**Violated Safety Categories**")
            for category in categories:
              st.warning(f"{category}")
          else:
            st.warning("No categories identified in the response.")
    except Exception as e:
      st.exception(f"Exception: {e}")
