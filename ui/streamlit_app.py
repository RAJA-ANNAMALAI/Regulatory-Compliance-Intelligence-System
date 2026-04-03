import streamlit as st
import requests
from datetime import datetime

# Set up Streamlit page 
st.set_page_config(
    page_title="Regulatory Compliance Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling  
st.markdown("""
<style>
    /* Hide unnecessary Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Main container styling */
    .main .block-container {
        padding-top: 2.5rem;
        padding-bottom: 2rem;
        max-width: 950px;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }

    /* Chat message styling */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarUser"]) {
        background-color: #4F46E5;
        color: white;
        margin-left: auto;
        margin-right: 0;
        max-width: 78%;
        border-radius: 12px 12px 4px 12px;
    }

    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarAssistant"]) {
        background-color: #1E2937;
        color: #E2E8F0;
        margin-left: 0;
        margin-right: auto;
        max-width: 82%;
        border-radius: 12px 12px 12px 4px;
    }

    .stChatMessage {
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Source footer */
    .source-text {
        font-size: 0.78rem;
        color: #94A3B8;
        margin-top: 0.8rem;
        padding-top: 0.6rem;
        border-top: 1px solid #334155;
    }

    /* Button styling */
    .stButton button {
        font-weight: 500;
        border-radius: 8px;
    }

    /* Welcome message card */
    .welcome-card {
        background-color: #f8fafc;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin: 1.5rem 0;
    }

    /* Disable button appearance */
    .disabled-button {
        cursor: not-allowed;
        background-color: #dcdcdc;
    }
</style>
""", unsafe_allow_html=True)

# Base URL for API calls
API_BASE_URL = "http://127.0.0.1:8000/api/v1" 

# Initialize session state variables if not already present
if "messages" not in st.session_state:
    st.session_state.messages = [] 

if "role" not in st.session_state:
    st.session_state.role = "User" 

with st.sidebar:
    st.markdown("### **Regulatory Compliance Intelligent system**")
    st.markdown("---")

    # Role selection
    role = st.radio(
        "Access Level",
        ["User", "Admin"],
        horizontal=False,
        label_visibility="visible"
    )
    st.session_state.role = role

    st.markdown("---")

    # Action buttons
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []  
        st.rerun()  # Rerun the app to refresh the state

    if st.session_state.messages:
        # Provide an option to download the chat
        chat_text = "\n\n".join([ 
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
            for m in st.session_state.messages
        ])
        st.download_button(
            label="Export Chat",
            data=chat_text,
            file_name=f"regucomply_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            use_container_width=True
        )

    st.markdown("---")

# Admin section for document management
if st.session_state.role == "Admin":
    st.title("Document Management")
    st.markdown("Upload regulatory documents to enhance the knowledge base.")

    col1, col2 = st.columns([3, 1])  
    with col1:
        uploaded_file = st.file_uploader(
            "Select Document",
            type=["pdf", "docx", "txt"],
            help="Supported formats: PDF, DOCX, TXT"
        )

    # Handle the file upload process
    if uploaded_file:
        st.info(f"**File:** {uploaded_file.name}  |  **Size:** {(uploaded_file.size / 1024):.1f} KB")

        # Check and handle upload state to avoid multiple uploads
        if "is_uploading" not in st.session_state:
            st.session_state.is_uploading = False  

        # Disable the button once file is being uploaded
        if st.session_state.is_uploading:
            st.button("Uploading...", disabled=True, use_container_width=True)  
        else:
            if st.button("Upload Document", type="primary", use_container_width=True):
                st.session_state.is_uploading = True 

                try:
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=60)

                    if response.status_code == 200:
                        st.success("Document uploaded successfully!")
                    else:
                        st.error(f"Upload failed: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

                st.session_state.is_uploading = False  # Reset upload state after completion

else:
    # User mode
    st.title("Regulatory Compliance Intelligence")
    st.markdown("Ask any question related to regulatory compliance, SEBI, RBI, Companies Act, etc.")

    chat_container = st.container()

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message.get("source"):
                    source = message["source"]
                    page_number = message.get("page_number", "N/A")  
                    st.markdown(
                        f'<div class="source-text">Source: {source} | Page: {page_number}</div>',
                        unsafe_allow_html=True
                    )

    if not st.session_state.messages:
        with chat_container:
            st.markdown("""
            <div class="welcome-card">
                <h4>Hello! 👋</h4>
                <p>I can help you with regulatory compliance queries for Indian financial markets.</p>
                <p><strong>Try asking:</strong></p>
                <ul>
                    <li>What are the disclosure requirements under SEBI LODR?</li>
                    <li>Summarize insider trading regulations</li>
                    <li>What are the compliance obligations for listed companies?</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # Chat input field 
    if prompt := st.chat_input("Ask a regulatory compliance question..."):
       
        st.session_state.messages.append({"role": "user", "content": prompt})

        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Assistant response
        with chat_container:
            with st.chat_message("assistant"):
                try:
                    # Send the query to the backend API for processing
                    response = requests.post(
                        f"{API_BASE_URL}/query",
                        json={"query": prompt},
                        timeout=40
                    )

                    if response.status_code == 200:
                        data = response.json()
                        results = data.get("results", [])

                        if results:
                            # Extract content and metadata (source and page number) from the response
                            answer = results[0].get("content", "No answer available.")
                            source = results[0].get("metadata", {}).get("source", "")
                            page_number = results[0].get("metadata", {}).get("page", "N/A")

                            st.markdown(answer)
                            if source:
                                st.markdown(
                                    f'<div class="source-text">Source: {source} | Page: {page_number}</div>',
                                    unsafe_allow_html=True
                                )

                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": answer,
                                "source": source,
                                "page_number": page_number
                            })
                        else:
                            no_result = "I couldn't find relevant information for your query."
                            st.markdown(no_result)
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": no_result
                            })
                    else:
                        error_msg = f"API Error: {response.status_code}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })

                except Exception as e:
                    error_msg = f"Connection error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })