import os
import glob
import time
from dotenv import load_dotenv

# Import our custom "MCP Servers" (The Tools)
from mcp_servers import document_parser, vision_analyst, librarian
# Import our utility (The Logic)
from utils import chunking

# Load environment variables (API Keys)
load_dotenv()

# Configuration
INPUT_FOLDER = "data/inputs"
PROCESSED_FOLDER = "data/processed"

def main():
    print("🚀 Starting PDF Extraction Agent...")
    
    # 1. Discovery: Find all PDFs
    pdf_files = glob.glob(os.path.join(INPUT_FOLDER, "*.pdf"))
    
    if not pdf_files:
        print(f"⚠️  No PDFs found in '{INPUT_FOLDER}'. Please add some files.")
        return

    print(f"📂 Found {len(pdf_files)} PDFs to process.\n")

    # 2. Main Loop: Process each PDF
    for pdf_path in pdf_files:
        process_single_pdf(pdf_path)

    print("\n✅ All jobs completed successfully!")

def process_single_pdf(pdf_path):
    filename = os.path.basename(pdf_path)
    print(f"--- 🔨 Processing: {filename} ---")

    try:
        # --- STEP 1: PARSING (Local MCP Tool) ---
        print("   [1/4] Parsing PDF layout & extracting images...")
        # Returns raw markdown and a list of image file paths
        raw_markdown, image_paths = document_parser.parse_pdf(pdf_path, output_dir=PROCESSED_FOLDER)
        
        
        # --- STEP 2: VISION ANALYSIS (Cloud MCP Tool) ---
        print(f"   [2/4] Analyzing {len(image_paths)} extracted images with Groq...")
        
        # We start with the raw markdown, and we will append our findings to it
        enriched_markdown = raw_markdown
        
        for img_path in image_paths:
            # OPTIMIZATION: Skip tiny images (like icons, lines, logos)
            # If file size is less than 5KB (5000 bytes), ignore it.
            if os.path.getsize(img_path) < 5000:
                continue
                
            try:
                print(f"       -> Analyzing image: {os.path.basename(img_path)}...")
                caption = vision_analyst.analyze_image(img_path)
                
                # INTELLIGENCE: Inject the finding back into the text
                # Ideally, we would replace the specific image tag, but appending 
                # is safer and ensures the LLM sees the data.
                enriched_markdown += f"\n\n> **[AI IMAGE ANALYSIS]**: The image '{os.path.basename(img_path)}' shows: {caption}\n"
                
                # Sleep briefly to respect Groq Rate Limits (important for Free Tier)
                time.sleep(2) 
                
            except Exception as e:
                print(f"       ⚠️  Vision Error on {img_path}: {e}")

        
        # --- STEP 3: CHUNKING (Local Logic) ---
        print("   [3/4] Intelligent Chunking...")
        chunks = chunking.chunk_markdown(enriched_markdown)
        print(f"       -> Created {len(chunks)} knowledge chunks.")


        # --- STEP 4: MEMORY STORAGE (Local MCP Tool) ---
        print("   [4/4] Saving to ChromaDB...")
        for i, chunk_text in enumerate(chunks):
            # Create a unique ID for the database
            chunk_id = f"{filename}_chunk_{i}"
            librarian.save_chunk(chunk_text, filename, chunk_id)
            
        print(f"   ✅ Finished processing {filename}")

    except Exception as e:
        print(f"   ❌ CRITICAL ERROR processing {filename}: {e}")

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs(INPUT_FOLDER, exist_ok=True)
    main()