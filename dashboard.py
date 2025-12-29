import streamlit as st
import chromadb
import pandas as pd

# Page Config
st.set_page_config(page_title="PDF Knowledge Base", layout="wide")
st.title("🧠 PDF Knowledge Base Viewer")

# 1. Connect to Database
@st.cache_resource
def get_client():
    return chromadb.PersistentClient(path="data/chromadb")

try:
    client = get_client()
    collection = client.get_collection("pdf_knowledge")
    
    # Sidebar Stats
    total_docs = collection.count()
    st.sidebar.header("Stats")
    st.sidebar.metric("Total Chunks", total_docs)
    
    # 2. Search Bar
    query = st.text_input("🔍 Search your database (Semantic Search)", placeholder="Type something like 'revenue Q3'...")
    
    if query:
        # Perform similarity search
        results = collection.query(
            query_texts=[query],
            n_results=5 # Return top 5 matches
        )
        
        st.subheader(f"Top Matches for: '{query}'")
        
        # Display results nicely
        for i in range(len(results['documents'][0])):
            doc_id = results['ids'][0][i]
            meta = results['metadatas'][0][i]
            content = results['documents'][0][i]
            score = results['distances'][0][i] # Lower score = better match in Chroma
            
            with st.expander(f"📄 Match {i+1} (Source: {meta.get('source', 'Unknown')})"):
                st.markdown(f"**Relevance Score:** {score:.4f}")
                st.info(content)
                st.caption(f"Chunk ID: {doc_id}")

    # 3. Browse Mode (If no search)
    else:
        st.subheader("🗂️ Browse Recent Chunks")
        # Get first 10 items
        data = collection.peek(limit=10)
        
        if data['ids']:
            # Create a nice table
            df = pd.DataFrame({
                'ID': data['ids'],
                'Source': [m.get('source') for m in data['metadatas']],
                'Preview': [d[:100] + "..." for d in data['documents']]
            })
            st.dataframe(df, use_container_width=True)
            
            st.info("👆 Use the search bar above to query the actual vectors.")
            
except Exception as e:
    st.error(f"Could not load database. Error: {e}")
    st.warning("Make sure the 'data/chromadb' folder exists and is not empty.")