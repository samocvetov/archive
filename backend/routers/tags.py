from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from models import Tag
from schemas import Tag as TagSchema, TagCreate
from database import get_db

router = APIRouter(prefix="/tags", tags=["tags"])

@router.post("/", response_model=TagSchema)
async def create_tag(tag: TagCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).where(Tag.name == tag.name.lower()))
    existing_tag = result.scalar_one_or_none()
    
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag already exists")
    
    new_tag = Tag(name=tag.name.lower())
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    
    return new_tag

@router.get("/", response_model=List[TagSchema])
async def get_tags(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Tag)
    
    if search:
        query = query.where(Tag.name.ilike(f"%{search.lower()}%"))
    
    query = query.offset(skip).limit(limit).order_by(Tag.name)
    
    result = await db.execute(query)
    tags = result.scalars().all()
    
    return tags

@router.get("/popular", response_model=List[dict])
async def get_popular_tags(
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    from models import fragment_tags
    
    query = (
        select(Tag, func.count(fragment_tags.c.fragment_id).label("count"))
        .join(fragment_tags)
        .group_by(Tag.id)
        .order_by(func.count(fragment_tags.c.fragment_id).desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    tags = result.all()
    
    return [{"id": tag[0].id, "name": tag[0].name, "count": tag[1]} for tag in tags]

@router.get("/{tag_id}", response_model=TagSchema)
async def get_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    return tag

@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    await db.delete(tag)
    await db.commit()
    
    return {"message": "Tag deleted successfully"}
