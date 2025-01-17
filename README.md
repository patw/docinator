# Docinator

Provides an API to input PDF files and convert to Markdown text, with some summarization options.  This is useful for chunking PDF for RAG chatbots.

## Local Installation

```
pip install -r requirements.txt
```

Copy the model.json.sample to model.json.  In here you can modify the BaseURL to work with any OAI compatible service or use your own local models.

## Running Docinator API

```
uvicorn main:app --host 0.0.0.0 --port 3009 --reload
```

## Accessing API

http://localhost:3009/docs
