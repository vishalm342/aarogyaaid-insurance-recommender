import fitz
from backend.rag.chunker import chunk_policy_document
from backend.db.mongo import mongo_db
from backend.config import settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import io

async def ingest_policy(file_bytes: bytes, filename: str, policy_name: str, insurer: str, policy_id: str):
    # Parse PDF
    pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
        
    # Chunk
    chunks = chunk_policy_document(text, policy_id, policy_name, insurer)
    
    if not chunks:
        return 0

    # Embed & Store
    embeddings = GoogleGenerativeAIEmbeddings(model=settings.embedding_model, google_api_key=settings.gemini_api_key)
    
    texts = [c["text"] for c in chunks]
    vectors = embeddings.embed_documents(texts)
    
    for i, c in enumerate(chunks):
        c["embedding"] = vectors[i]
        
    await mongo_db.chunks_collection.insert_many(chunks)
    
    return len(chunks)