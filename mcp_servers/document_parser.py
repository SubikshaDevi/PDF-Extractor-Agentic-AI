import os
import pymupdf4llm

def parse_pdf(pdf_path, output_dir="data/processed"):
    """
    Input: Path to raw PDF.
    Output: Returns Markdown text and saves images to disk.
    """
    print(f"📄 Parsing with PyMuPDF: {pdf_path}...")
    
    fname = os.path.basename(pdf_path).replace(".pdf", "")
    save_path = os.path.join(output_dir, fname)
    os.makedirs(save_path, exist_ok=True)

    # Convert PDF to Markdown + Extract Images in one go
    # "write_images=True" automatically extracts images to the folder
    md_text = pymupdf4llm.to_markdown(
        pdf_path,
        write_images=True,
        image_path=save_path,  # Where to save images
        image_format="png"
    )

    # Helper: Find all the images it just saved
    image_paths = [
        os.path.join(save_path, f) 
        for f in os.listdir(save_path) 
        if f.endswith(".png")
    ]

    # Save the full markdown for inspection
    with open(f"{save_path}/full.md", "w", encoding="utf-8") as f:
        f.write(md_text)
        
    return md_text, image_paths