# Part 21: LLM Applications

---

## Chapter 1: RAG Architecture & AI Resume Analyzer

### 1. Introduction
Large Language Models (LLMs) enable intelligent, natural-language API operations. Retrieval-Augmented Generation (RAG) is an architectural pattern that retrieves relevant external documents (e.g. from vector databases) and injects them into the LLM prompt, allowing the model to answer queries based on custom, private datasets.

### 2. Concept Explanation
* **Why it exists**: LLMs are static and have cut-off dates. RAG connects real-time data or internal corporate files (like PDFs) to the model without expensive retraining.
* **When to use it**: Q&A bots, resume parsers, policy search engines, customer support interfaces.
* **When NOT to use it**: Simple text classification that can be solved with traditional NLP models or when strict deterministic answers are required.
* **Advantages**: No retraining required, factual accuracy (mitigates hallucinations), secure integration with internal databases.
* **Disadvantages**: Latency overhead (network calls to vector databases and LLM APIs), tokens consumption cost.
* **Industry Use Cases**: Enterprise knowledge management, CV parsing, customer service bots.

### 3. Architecture Explanation
The architecture extracts text from uploaded documents, generates embeddings, stores them in a Vector Database, and queries the LLM using retrieved document context.
```
Uploaded PDF ---> Text Chunking ---> Embeddings API ---> Vector Database (Index)
Query ---> Vector Search (Retrieval) ---> Prompt Assembly ---> LLM API ---> Response
```

### 4. Visual Workflow
```
User Query ---> Search Vector DB ---> Retrieve top 3 matches ---> Build Context ---> Query Gemini/OpenAI
```

### 5. Real-World Scenario
An HR department needs an AI Resume Analyzer API. Users upload a candidate resume PDF, and the API parses the text, saves it to a vector index, and allows recruiters to ask natural-language questions about the candidate's qualifications.

### 6. Step-by-Step Implementation
1. Install AI libraries: `openai`, `langchain`, `pypdf`.
2. Configure OpenAI/Gemini API credentials.
3. Build a document processing pipeline (chunking, embedding, index).
4. Implement endpoints for file upload and document Q&A.

### 7. Source Code Examples
```python
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(title="AI Resume Analyzer & Q&A Portal")

# Mock Vector Database
class MockVectorDB:
    def __init__(self):
        self.storage = {}

    def add_document(self, doc_id: str, text: str):
        self.storage[doc_id] = text

    def retrieve_context(self, doc_id: str, query: str) -> str:
        # Simple string-matching mock for vector search
        content = self.storage.get(doc_id, "")
        words = query.lower().split()
        sentences = content.split(".")
        matched = [s.strip() for s in sentences if any(w in s.lower() for w in words)]
        return ". ".join(matched[:3]) if matched else content[:1000]

vdb = MockVectorDB()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "mock-key")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

class QueryPayload(BaseModel):
    document_id: str
    question: str

@app.post("/upload-resume")
async def upload_resume(document_id: str, file: UploadFile = File(...)):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only plain text files (.txt) are supported in this demo")
    
    # Read resume text
    contents = await file.read()
    resume_text = contents.decode("utf-8")
    
    # Store in the vector database
    vdb.add_document(document_id, resume_text)
    return {"document_id": document_id, "status": "indexed", "bytes_read": len(resume_text)}

@app.post("/query-resume")
async def query_resume(payload: QueryPayload):
    # 1. Retrieve relevant text chunks from the vector database
    context = vdb.retrieve_context(payload.document_id, payload.question)
    
    if not context:
        raise HTTPException(status_code=404, detail="Document not found or empty")

    # 2. Assemble the prompt context
    system_prompt = "You are an assistant analyzing candidate resumes. Use the provided context to answer the question."
    user_prompt = f"Resume Context:\n{context}\n\nQuestion: {payload.question}"
    
    # 3. Call the LLM API (OpenAI example)
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    json_payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2
    }

    # If running with mock keys, mock the response to avoid network failures
    if OPENAI_API_KEY == "mock-key":
        return {
            "answer": f"[MOCK ANSWER] Based on the context: {context[:100]}... The candidate is highly qualified.",
            "document_id": payload.document_id
        }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(OPENAI_URL, headers=headers, json=json_payload, timeout=30.0)
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail=f"LLM Gateway Error: {response.text}")
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            return {"answer": answer, "document_id": payload.document_id}
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Failed to connect to LLM provider: {e}")
```

### 8. API Testing Examples
1. Upload a candidate resume text:
```bash
echo "John Doe has 5 years of experience building APIs with FastAPI and Python." > john_resume.txt
curl -X POST "http://127.0.0.1:8000/upload-resume?document_id=john-doe" \
  -F "file=@john_resume.txt"
# Response: {"document_id":"john-doe","status":"indexed","bytes_read":72}
```
2. Query the resume about Python experience:
```bash
curl -X POST http://127.0.0.1:8000/query-resume \
  -H "Content-Type: application/json" \
  -d '{"document_id": "john-doe", "question": "Does he know Python?"}'
# Response: {"answer":"[MOCK ANSWER] Based on the context: John Doe has 5 years of experience building APIs with FastAPI and Python...","document_id":"john-doe"}
```

### 9. Common Mistakes
Sending un-truncated documents directly to LLM endpoints, causing high token costs or exceeding token context windows.

### 10. Best Practices
Set token limits, split documents into overlapping chunks (e.g. 500 characters with 50-character overlaps), and run similarity searches to send only relevant context to the LLM.

### 11. Interview Questions
* **Q: What is the benefit of RAG over fine-tuning a model?**
  * *A*: Fine-tuning updates the model's weights but is expensive, slow, and prone to hallucinations. RAG keeps the model static and feeds it relevant, verifiable documents directly in the prompt, making it easy to update data and track sources.

### 12. Chapter Summary
RAG injects retrieved database context into LLM prompts to provide accurate, data-driven answers. FastAPI integrates with vector databases and LLM APIs to build responsive AI services.

### 13. Practice Exercises
Extend the API to accept a list of multiple candidate resume IDs and compare their years of experience using a single query.
