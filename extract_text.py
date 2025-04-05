import json
from PyPDF2 import PdfReader

# Remove OceanofPDF trademark
def remove_trademark(content: str) -> str:
    return content.replace("OceanofPDF.com", "")

index = None
with open("index.json", "r") as f:
    index = json.load(f)
print(index)

# Open the PDF file (make sure the file path is correct)
reader = PdfReader("sample.pdf")
#print(len(reader.pages))

# Loop over each page and print its text content
for key, value in index.items():
    content = ""
    start = value["start"]
    end = value["end"]
    for page in range(start, end+1):
        content += reader.pages[page].extract_text()
    #content += '\n'
    content = remove_trademark(content)
    with open(f"{key}.txt", "w") as f:
        f.write(content)







