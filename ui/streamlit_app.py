import streamlit as st
import requests
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Regulatory Compliance System",
    page_icon="",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    
    [data-testid="stSidebar"] {
        background-color: #fafbfc;
        border-right: 1px solid #e9ecef;
        padding: 2rem 1rem;
    }
    
    .stChatMessage {
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 8px;
    }
    
    .reference {
        font-size: 0.75rem;
        color: #6c757d;
        margin-top: 0.75rem;
        padding-top: 0.75rem;
        border-top: 1px solid #e9ecef;
    }
    
    .page-title {
        font-size: 1.8rem;
        font-weight: 500;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    .page-description {
        font-size: 0.9rem;
        color: #6c757d;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e9ecef;
    }
    
    .admin-header {
        font-size: 1.5rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    
    .status-connected {
        color: #28a745;
        font-size: 0.8rem;
    }
    
    .status-disconnected {
        color: #dc3545;
        font-size: 0.8rem;
    }
    
    hr {
        margin: 1rem 0;
    }
    
    button {
        font-weight: 400;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "role" not in st.session_state:
    st.session_state.role = "User"

# Sidebar
with st.sidebar:
    st.markdown("### Regulatory Compliance")
    st.markdown("Intelligent System")
    st.markdown("---")
    
    st.markdown("**Access Mode**")
    role = st.radio("", ["User", "Admin"], label_visibility="collapsed")
    st.session_state.role = role
    
    st.markdown("---")
    
    st.markdown("**Conversation**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    if st.session_state.messages:
        with col2:
            chat_text = "\n\n".join([
                f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
                for m in st.session_state.messages
            ])
            st.download_button(
                label="Export",
                data=chat_text,
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                use_container_width=True
            )
    
    st.markdown("---")
    
    st.markdown("**System Status**")
    try:
        requests.post(f"{API_BASE_URL}/query", json={"query": "test"}, timeout=2)
        st.markdown('<p class="status-connected">● Connected</p>', unsafe_allow_html=True)
    except:
        st.markdown('<p class="status-disconnected">● Disconnected</p>', unsafe_allow_html=True)
        st.caption("Start backend on port 8000")

# Main content
if st.session_state.role == "Admin":
    st.markdown('<div class="admin-header">Document Upload</div>', unsafe_allow_html=True)
    st.markdown("Add documents to the knowledge base")
    
    uploaded_file = st.file_uploader("Select file", type=["pdf", "docx", "txt"])
    
    if uploaded_file:
        st.info(f"File: {uploaded_file.name} ({(uploaded_file.size / 1024):.1f} KB)")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Upload", type="primary", use_container_width=True):
                try:
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=60)
                    
                    if response.status_code == 200:
                        st.success(f"Successfully uploaded {uploaded_file.name}")
                    else:
                        st.error(f"Upload failed: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.rerun()

else:
    st.markdown('<div class="page-title">Regulatory Compliance Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-description">Ask questions about regulations, compliance requirements, and guidelines</div>', unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message.get("source"):
                    st.markdown(f'<div class="reference">Source: {message["source"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Type your question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            try:
                response = requests.post(
                    f"{API_BASE_URL}/query",
                    json={"query": prompt},
                    timeout=30
                )
                
                message_placeholder.empty()
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    if results:
                        answer = results[0].get("content", "No answer available")
                        source = results[0].get("metadata", {}).get("source", "")
                        
                        st.markdown(answer)
                        if source:
                            st.markdown(f'<div class="reference">Source: {source}</div>', unsafe_allow_html=True)
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "source": source
                        })
                    else:
                        response_text = "No relevant information found."
                        st.markdown(response_text)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_text
                        })
                else:
                    error_msg = f"API Error: {response.status_code}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
                    
            except requests.exceptions.ConnectionError:
                message_placeholder.empty()
                error_msg = "Cannot connect to backend server."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
            except Exception as e:
                message_placeholder.empty()
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
    
    # Welcome message
    if not st.session_state.messages:
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown("""
                Hello. I can help you with regulatory compliance questions.
                
                **Examples:**
                - What are the disclosure requirements?
                - Summarize key compliance obligations
                - What regulations apply in this context?
                
                Upload documents in Admin mode to enhance the knowledge base.
                """)