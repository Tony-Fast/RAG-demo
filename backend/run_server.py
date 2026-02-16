"""
Simple RAG Server - Without auto-reload
"""
import uvicorn
import sys

print("=" * 60)
print("Starting RAG Knowledge Base Server...")
print("=" * 60)
print()

try:
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
except Exception as e:
    print()
    print("=" * 60)
    print("ERROR:")
    print("=" * 60)
    print(str(e))
    print()
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
