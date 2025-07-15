import json
import os
from PyPDF2 import PdfReader
from constants import PARSED_TEXT_FOLDER_NAME

# Remove OceanofPDF trademark
def remove_trademark(content: str) -> str:
    return content.replace("OceanofPDF.com", "")

def get_index(file_path: str) -> dict:
    index = None
    with open(file_path, "r") as f:
        index = json.load(f)
    print(index)
    return index

def extract_organize_pages(pdf_name: str, index_file_name: str) -> None:
    # Open the PDF file (make sure the file path is correct)
    reader = PdfReader(pdf_name)
    print(f"Total number of pages: {len(reader.pages)}")

    index = get_index(index_file_name)

    os.makedirs(PARSED_TEXT_FOLDER_NAME, exist_ok=True)

    # Loop over each page and print its text content
    for key, value in index.items():
        content = ""
        start = value["start"]
        end = value["end"]
        for page in range(start, end+1):
            content += reader.pages[page].extract_text()
        content = remove_trademark(content)
        with open(f"{PARSED_TEXT_FOLDER_NAME}/{key}.txt", "w") as f:
            f.write(content)

if __name__ == "__main__":
    extract_organize_pages("sample.pdf", "index.json")






