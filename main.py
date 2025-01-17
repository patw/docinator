from fastapi import FastAPI, UploadFile
from docling.document_converter import DocumentConverter
import json
import tempfile

# Use local models with the OpenAI library and a custom baseurl
from openai import OpenAI

# Load the llm config from the json file provided on command line
with open("model.json", 'r') as file:
    llm_config = json.load(file)

DEFAULT_SYSTEM = "You are a helpful assistant who will always answer the question with only the data provided"
DEFAULT_SUMMARY_PROMPT = "{data}\n\nRewrite the above document into plain text"
DEFAULT_FACT_PROMPT = "{data}\n\nSummarize the above document into facts, one per line bullet point"
DEFAULT_TEMP = 0.1 # very mild temp for more boring results

# Fast API init
app = FastAPI(
        title="Docinator",
        description="Feed me documents and I'll give you Markdown",
        version="1.0",
        contact={
            "name": "Pat Wendorf",
            "email": "pat.wendorf@mongodb.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/license/mit/",
    }
)

converter = DocumentConverter()

# Call llm using the llm configuration
def llm_local(prompt):
    client = OpenAI(api_key=llm_config["api_key"], base_url=llm_config["base_url"])
    messages=[{"role": "system", "content": DEFAULT_SYSTEM},{"role": "user", "content": prompt}]
    response = client.chat.completions.create(model=llm_config["model"], temperature=DEFAULT_TEMP, messages=messages)
    return response.choices[0].message.content

@app.post("/doc_url", summary="Parse a PDF from a URL and output Markdown", description="Takes a URL to a PDF file as input, and optionally allows LLM summarization or fact extraction")
async def doc_url(source_url: str, llm_summary: bool = False, llm_facts: bool = False):
    result = converter.convert(source_url)
    md_result = result.document.export_to_markdown()
    if llm_summary:
        prompt = DEFAULT_SUMMARY_PROMPT.format(data=md_result)
        return llm_local(prompt)
    if llm_facts:
        prompt = DEFAULT_FACT_PROMPT.format(data=md_result)
        return llm_local(prompt)
    return md_result

@app.post("/doc_upload", summary="Parse a PDF from a file upload and output Markdown", description="Takes a PDF file as input and outputs Markdown. Optionally allows LLM summarization or fact extraction")
async def doc_upload(file: UploadFile, llm_summary: bool = False, llm_facts: bool = False):
    # Save the file to the /tmp directory
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name
        temp_file.write(await file.read())
        result = converter.convert(file_path)
        md_result = result.document.export_to_markdown()
        if llm_summary:
            prompt = DEFAULT_SUMMARY_PROMPT.format(data=md_result)
            return llm_local(prompt)
        if llm_facts:
            prompt = DEFAULT_FACT_PROMPT.format(data=md_result)
            return llm_local(prompt)
        return md_result