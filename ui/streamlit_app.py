import streamlit as st
import requests
from datetime import datetime

st.set_page_config(
    page_title="REGULATORY COMPLIANCE INTELLIGENCE SYSTEM",
    layout="wide"
)

# Initialize session state (kept minimal since history tab is removed)
if "last_results" not in st.session_state:
    st.session_state.last_results = None

st.title("REGULATORY COMPLIANCE INTELLIGENCE SYSTEM")

st.header("Ask Questions")

query = st.text_area(
    "Enter your query",
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
                    
                    # Store last result
                    st.session_state.last_results = data
                    st.session_state.last_query = query.strip()

                    st.subheader("Results")

                    for i, res in enumerate(data.get("results", []), 1):
                        with st.expander(f"Result {i}", expanded=True):
                            # Query
                            st.markdown("**Query**")
                            st.info(query)

                            # Answer
                            st.markdown("**Answer**")
                            st.write(res.get("content", "No content available"))

                            # Page and Confidence in columns
                            col1, col2 = st.columns(2)

                            with col1:
                                st.markdown("**Page**")
                                page_info = res.get("metadata", {}).get("page", "N/A")
                                st.write(page_info)

                            with col2:
                                st.markdown("**Confidence Score**")
                                confidence = res.get("metadata", {}).get("confidence", 0.0)
                                
                                if isinstance(confidence, (int, float)):
                                    conf_pct = confidence * 100 if confidence <= 1.0 else confidence
                                    st.write(f"{conf_pct:.1f}%")
                                else:
                                    st.write(confidence)

                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend. Is the API running on http://127.0.0.1:8000/api/v1/query")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a query.")

# Show last search again if available (useful when switching tabs or refreshing)
if st.session_state.last_results:
    st.divider()
    st.subheader("Last Search Results")
    
    for i, res in enumerate(st.session_state.last_results.get("results", []), 1):
        with st.expander(f"Last Search - Result {i}"):
            st.markdown("**Query**")
            st.info(st.session_state.last_query)

            st.markdown("**Answer**")
            st.write(res.get("content", "No content available"))

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Page**")
                page_info = res.get("metadata", {}).get("page", "N/A")
                st.write(page_info)

            with col2:
                st.markdown("**Confidence Score**")
                confidence = res.get("metadata", {}).get("confidence", 0.0)
                if isinstance(confidence, (int, float)):
                    conf_pct = confidence * 100 if confidence <= 1.0 else confidence
                    st.write(f"{conf_pct:.1f}%")
                else:
                    st.write(confidence)