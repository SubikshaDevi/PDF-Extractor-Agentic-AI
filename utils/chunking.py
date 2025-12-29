from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

def chunk_markdown(markdown_text):
    """
    Intelligently splits markdown text into meaningful chunks.
    """
    
    # 1. Define the headers we want to split by
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    # 2. First Pass: Split by semantic headers
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(markdown_text)

    # 3. Second Pass: If a section is still too big (e.g. > 1000 chars), split it by character
    # This prevents one massive section from overflowing the LLM context window.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    
    final_chunks = text_splitter.split_documents(md_header_splits)
    
    # Convert back to simple list of strings for ChromaDB
    # We combine the content with the header metadata for better context
    processed_chunks = []
    for chunk in final_chunks:
        header_context = ""
        if "Header 1" in chunk.metadata:
            header_context += f"{chunk.metadata['Header 1']} > "
        if "Header 2" in chunk.metadata:
            header_context += f"{chunk.metadata['Header 2']} > "
            
        full_content = f"Context: {header_context}\nContent: {chunk.page_content}"
        processed_chunks.append(full_content)

    return processed_chunks