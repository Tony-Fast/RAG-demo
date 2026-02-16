"""Debug document upload step by step"""
import asyncio
import sys
sys.path.insert(0, 'backend')

import os

print("=" * 70)
print("DEBUGGING DOCUMENT UPLOAD (ASYNC)")
print("=" * 70)

async def main():
    # Step 1: Import services
    print("\n[Step 1] Importing services...")
    try:
        from app.core.config import settings
        from app.services.document_processor import document_processor
        from app.services.vector_store import vector_store
        from app.services.tfidf_embedding_service import embedding_service
        print("    ✓ All imports successful")
    except Exception as e:
        print(f"    ✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 2: Clear vector store
    print("\n[Step 2] Clearing vector store...")
    try:
        vector_store.clear()
        print("    ✓ Vector store cleared")
    except Exception as e:
        print(f"    ✗ Clear failed: {e}")
        import traceback
        traceback.print_exc()

    # Step 3: Create test document
    print("\n[Step 3] Creating test document...")
    test_content = """面试常见问题

1. 请介绍一下你自己
2. 你的优点是什么
3. 你的缺点是什么
4. 为什么选择我们公司
5. 你的职业规划是什么
"""
    test_file = "debug_test.txt"
    try:
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        print(f"    ✓ Created: {test_file}")
    except Exception as e:
        print(f"    ✗ Create failed: {e}")
        return

    # Step 4: Process document (ASYNC!)
    print("\n[Step 4] Processing document...")
    try:
        document, chunks = await document_processor.process_document(test_file, test_file)
        print(f"    ✓ Document processed: {document.id}")
        print(f"    ✓ Status: {document.status}")
        print(f"    ✓ Chunks: {len(chunks)}")
        for i, chunk in enumerate(chunks):
            print(f"      - Chunk {i}: {chunk.content[:50]}...")
    except Exception as e:
        print(f"    ✗ Process failed: {e}")
        import traceback
        traceback.print_exc()
        os.remove(test_file)
        return

    # Step 5: Generate embeddings
    print("\n[Step 5] Generating embeddings...")
    try:
        texts = [chunk.content for chunk in chunks]
        print(f"    ✓ Texts count: {len(texts)}")
        embeddings = embedding_service.encode(texts, show_progress=False)
        print(f"    ✓ Embeddings shape: {embeddings.shape}")
    except Exception as e:
        print(f"    ✗ Embedding failed: {e}")
        import traceback
        traceback.print_exc()
        os.remove(test_file)
        return

    # Step 6: Add to vector store
    print("\n[Step 6] Adding to vector store...")
    try:
        vector_store.add_chunks(chunks, embeddings)
        stats = vector_store.get_stats()
        print(f"    ✓ Added successfully!")
        print(f"    ✓ Stats: {stats}")
    except Exception as e:
        print(f"    ✗ Add failed: {e}")
        import traceback
        traceback.print_exc()
        os.remove(test_file)
        return

    # Step 7: Test search
    print("\n[Step 7] Testing search...")
    try:
        results = vector_store.search_by_text("职业规划", top_k=2)
        print(f"    ✓ Search found {len(results)} results")
        for r in results:
            print(f"      - Score: {r.similarity_score:.4f}")
            print(f"        Content: {r.content[:50]}...")
    except Exception as e:
        print(f"    ✗ Search failed: {e}")
        import traceback
        traceback.print_exc()

    # Step 8: Cleanup
    print("\n[Step 8] Cleaning up...")
    os.remove(test_file)
    print("    ✓ Cleanup complete")

    print("\n" + "=" * 70)
    print("SUCCESS! Document upload pipeline works correctly.")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
