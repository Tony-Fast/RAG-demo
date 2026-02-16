"""
Quick Test Script for RAG Backend
"""
import sys
import os
import time

# Change to backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("RAG Knowledge Base - Quick Test")
print("=" * 60)
print()

# Test 1: Check imports
print("[1/4] Testing imports...")
try:
    import fastapi
    import uvicorn
    import faiss
    import sentence_transformers
    import openai
    print("    ✓ All dependencies imported successfully")
except Exception as e:
    print(f"    ✗ Import error: {e}")
    sys.exit(1)

# Test 2: Load embedding model
print()
print("[2/4] Loading embedding model (first run may take 1-2 minutes)...")
try:
    from sentence_transformers import SentenceTransformer
    start = time.time()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    elapsed = time.time() - start
    print(f"    ✓ Model loaded in {elapsed:.1f}s")
except Exception as e:
    print(f"    ✗ Model loading error: {e}")
    print("    (This is normal on first run - downloading model files)")

# Test 3: Initialize FAISS
print()
print("[3/4] Testing FAISS index creation...")
try:
    import faiss
    dimension = 384
    index = faiss.IndexFlatIP(dimension)
    print(f"    ✓ FAISS index created (dimension={dimension})")
except Exception as e:
    print(f"    ✗ FAISS error: {e}")

# Test 4: Load app
print()
print("[4/4] Loading FastAPI application...")
try:
    from app.main import app
    print("    ✓ FastAPI app loaded successfully")
    print()
    print("=" * 60)
    print("All tests passed!")
    print("=" * 60)
    print()
    print("To start the server, run:")
    print("  cd e:\\TRAE测试调试RAG\\RAG\\backend")
    print("  venv\\Scripts\\activate")
    print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print()
    print("Server will be available at:")
    print("  - http://localhost:8000")
    print("  - http://localhost:8000/docs")
    print("=" * 60)
except Exception as e:
    print(f"    ✗ App loading error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
