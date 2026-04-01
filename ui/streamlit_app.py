import streamlit as st
import requests

st.set_page_config(
    page_title="REGULATORY COMPLIANCE INTELLIGENCE SYSTEM",
    layout="wide"
)

# Initialize session state for query history
if "last_results" not in st.session_state:
    st.session_state.last_results = None

if "queries" not in st.session_state:
    st.session_state.queries = []

# Sidebar for role selection
role = st.sidebar.selectbox("Select Role", ["User", "Admin"])

st.title("REGULATORY COMPLIANCE INTELLIGENCE SYSTEM")

# Role-based UI layout
if role == "Admin":
    # Admin can upload documents
    st.sidebar.header("Admin Section")

    document = st.file_uploader("Upload Document", type=["pdf", "docx", "txt"])

    if document:
        with st.spinner("Uploading document..."):
            try:
                upload_payload = {"file": document}
                response = requests.post("http://localhost:8000/api/v1/upload", files=upload_payload)
                
                if response.status_code == 200:
                    st.success("Document uploaded successfully!")
                else:
                    st.error(f"Failed to upload document. {response.status_code}: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {str(e)}")

elif role == "User":
    # User can ask queries
    st.sidebar.header("User Section")
    st.header("Ask Questions")

    query = st.text_area(
        "Enter your question",
        placeholder="What are the mandatory disclosures under SEBI LODR for related party transactions?",
        height=120
    )

    if st.button("Search", type="primary"):
        if query.strip():
            with st.spinner("Thinking..."):
                try:
                    payload = {"query": query.strip()}

                    response = requests.post(
                        "http://127.0.0.1:8000/api/v1/query",
                        json=payload,
                        timeout=30
                    )

                    if response.status_code == 200:
                        data = response.json()

                        # Store query and result in session state
                        st.session_state.queries.append({"query": query.strip(), "results": data.get("results", [])})

                    else:
                        st.error(f"API Error: {response.status_code} - {response.text}")

                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend. Is the API running on http://127.0.0.1:8000/api/v1/query")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a query.")

    # Display previous queries and results for the user
    if st.session_state.queries:
        st.divider()
        st.subheader("Search History")

        # Only show the first (or the only) result without "Result 1" etc.
        for entry in st.session_state.queries:
            query = entry["query"]
            results = entry["results"]
            
            if results:  # If there is at least one result
                st.markdown("**Question**")
                st.info(query)

                # Just show the first (and only) result
                res = results[0]  # Assuming there is only one result
                st.markdown("**Answer**")
                st.write(res.get("content", "No content available"))

                # Page and Source columns (if available)
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Page**")
                    page_info = res.get("metadata", {}).get("page", "N/A")
                    st.write(page_info)

                with col2:
                    st.markdown("**Source**")
                    source_info = res.get("metadata", {}).get("source", "N/A")
                    st.write(source_info)
            else:
                st.write("No results found.")