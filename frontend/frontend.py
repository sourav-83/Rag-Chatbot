import streamlit as st
import requests
import base64
from pathlib import Path

# streamlit run frontend/frontend.py

st.set_page_config(page_title="RAG Chatbot", page_icon="💬", layout="centered")

image_path = Path(__file__).parent / "logo.png"  
with open(image_path, "rb") as img_file:
    encoded_string = base64.b64encode(img_file.read()).decode()


page_bg_img = f'''
<style>
.stApp {{
  background-image: url("data:image/jpg;base64,{encoded_string}");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
}}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

st.markdown('<h1>🤖 RAG Chatbot (BUET Assistant)</h1>', unsafe_allow_html=True)



question = st.text_input("", placeholder="Ask any question here...")
st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

if st.button("Ask"):
    if question.strip() == "":
        st.warning("Please enter a valid question.")
    else:
        try:
            with st.spinner("Thinking..."):
                response = requests.post(
                    "http://localhost:8000/main",  
                    json={"question": question}
                )

                if response.status_code == 200:
                    answer = response.json().get("answer")
                    st.success("✅ Answer:")
                    st.markdown(answer)
                else:
                    st.error(f"Error: {response.status_code} — {response.text}")

        except Exception as e:
            st.error(f"Request failed: {str(e)}")
