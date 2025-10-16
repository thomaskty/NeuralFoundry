from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
import uuid, shutil, os, asyncio, tempfile
import aiofiles

from app.db.database import get_db
from app.db.models import KnowledgeBase, User, KBChunk
from app.services.kb_ingestion_service import process_kb_file
from app.models.schemas import KnowledgeBaseCreate

router = APIRouter()

# -------------------------------------------------------------------------
# 1. Create Knowledge Base : validated
# -------------------------------------------------------------------------
@router.post("/users/{user_id}/knowledge-bases", status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
        user_id: str,
        payload: KnowledgeBaseCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    Create a new knowledge base for a given user.
    """
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    kb = KnowledgeBase(
        user_id=user_id,
        title=payload.title,
        description=payload.description
    )
    db.add(kb)
    await db.commit()
    await db.refresh(kb)

    return {
        "kb_id": str(kb.id),
        "user_id": str(user_id),
        "title": kb.title,
        "description": kb.description,
        "created_at": kb.created_at
    }


# -------------------------------------------------------------------------
# 2. Upload a file to Knowledge Base (async ingestion)
# -------------------------------------------------------------------------
@router.post("/knowledge-bases/{kb_id}/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_file_to_kb(
        kb_id: str,
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db)
):
    """
    Upload a file to the KB. Embedding ingestion runs asynchronously.
    """
    # Verify KB exists before accepting file
    kb_result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.id == kb_id))
    kb = kb_result.scalars().first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    # Check if filename already exists in this KB
    from app.db.models import KBDocument
    existing_doc = await db.execute(
        select(KBDocument).where(
            KBDocument.kb_id == kb_id,
            KBDocument.filename == file.filename
        )
    )
    if existing_doc.scalars().first():
        raise HTTPException(
            status_code=409,
            detail=f"File '{file.filename}' already exists in this knowledge base"
        )

    # Save uploaded file to system temp directory with unique prefix to avoid collisions
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"{kb_id}_{uuid.uuid4().hex[:8]}_{file.filename}")

    # Write file asynchronously
    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    # Add async background task, passing original filename
    background_tasks.add_task(process_kb_file, kb_id, file_path, file.filename)

    return {"message": f"File '{file.filename}' accepted for ingestion", "kb_id": kb_id}


# -------------------------------------------------------------------------
# 3. List all KBs per user
# -------------------------------------------------------------------------
@router.get("/users/{user_id}/knowledge-bases")
async def list_user_kbs(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    List all knowledge bases created by a specific user.
    """
    result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.user_id == user_id))
    kbs = result.scalars().all()

    return [
        {
            "kb_id": str(kb.id),
            "title": kb.title,
            "description": kb.description,
            "created_at": kb.created_at
        }
        for kb in kbs
    ]


# -------------------------------------------------------------------------
# 4. Delete a Knowledge Base
# -------------------------------------------------------------------------
@router.delete("/knowledge-bases/{kb_id}", status_code=status.HTTP_200_OK)
async def delete_kb(kb_id: str, db: AsyncSession = Depends(get_db)):
    """
    Delete a knowledge base and all its chunks.
    """
    kb_result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.id == kb_id))
    kb = kb_result.scalars().first()

    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    await db.delete(kb)
    await db.commit()

    return {"message": f"Knowledge base {kb_id} deleted"}