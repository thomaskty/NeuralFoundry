# app/services/kb_ingestion_service.py
import os
import aiofiles
import shutil
import hashlib
import asyncio
from datetime import datetime, timezone
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.db.models import KnowledgeBase, KBDocument, KBChunk
from app.services.embedding.huggingface_embedding import EmbeddingClient
from app.services.utils.kb_utils import chunk_text

embedding_client = EmbeddingClient()


async def process_kb_file(kb_id, file_path, original_filename):
    """
    Process uploaded file: read, chunk, embed, and store in database.
    This runs asynchronously in the background.

    Args:
        kb_id: Knowledge base UUID
        file_path: Temporary file path (will be deleted after processing)
        original_filename: Original filename from user upload
    """
    async with AsyncSessionLocal() as db:
        try:
            # 1. Verify KB exists
            kb_result = await db.execute(
                select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
            )
            kb = kb_result.scalars().first()

            if not kb:
                raise ValueError(f"KnowledgeBase {kb_id} not found")

            # 2. Read file asynchronously
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()

            # 3. Compute hash for deduplication
            text_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            text_size = len(content.encode("utf-8"))

            # 4. Create KBDocument entry
            document = KBDocument(
                kb_id=kb_id,
                uploaded_by=kb.user_id,
                filename=original_filename,  # Store original filename without ID prefix
                mime_type="text/plain",
                text_sha256=text_hash,
                text_size=text_size,
                doc_metadata={"source": original_filename},
                created_at=datetime.now(timezone.utc),
            )
            db.add(document)
            await db.flush()  # Async flush to get document.id

            # CRITICAL: Capture document.id and filename NOW before commit
            document_id = document.id
            document_filename = document.filename

            # 5. Chunk text
            chunks = chunk_text(content)

            # 6. Generate batch embeddings (run in executor if blocking)
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                embedding_client.get_batch_embeddings,
                chunks
            )

            # 7. Store each chunk
            kb_chunk_objects = [
                KBChunk(
                    kb_id=kb_id,
                    document_id=document_id,  # Use captured ID
                    chunk_index=i,
                    text=chunk,
                    token_count=len(chunk.split()),
                    embedding=emb.tolist(),
                    created_at=datetime.now(timezone.utc),
                )
                for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
            ]

            db.add_all(kb_chunk_objects)
            await db.commit()  # Async commit

            # Clean up temp file
            if os.path.exists(file_path):
                os.remove(file_path)

            # Return using captured values (not document object)
            return {
                "kb_id": kb_id,
                "document_id": str(document_id),
                "chunks_added": len(kb_chunk_objects),
                "message": f"Document '{document_filename}' processed successfully."
            }

        except Exception as e:
            await db.rollback()
            # Clean up temp file on error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e