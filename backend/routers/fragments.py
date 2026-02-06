from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
import os
from pathlib import Path

from config import settings
from models import Video, Fragment, Tag, fragment_tags
from schemas import FragmentCreate, FragmentUpdate, Fragment as FragmentSchema, FragmentWithTags
from services.ffmpeg_service import ffmpeg_service
from database import get_db

# Router for video-specific fragment operations
router = APIRouter(prefix="/videos/{video_id}/fragments", tags=["fragments"])

# Separate router for global fragment operations
global_router = APIRouter(prefix="/fragments", tags=["fragments"])

@global_router.get("/search", response_model=List[FragmentWithTags])
async def search_fragments_global(
    query: str,
    db: AsyncSession = Depends(get_db)
):
    """Search fragments across all videos by name or description"""
    stmt = (
        select(Fragment)
        .options(selectinload(Fragment.tags), selectinload(Fragment.video))
        .where(
            or_(
                Fragment.name.ilike(f"%{query}%"),
                Fragment.description.ilike(f"%{query}%")
            )
        )
        .order_by(Fragment.created_at.desc())
    )
    
    result = await db.execute(stmt)
    fragments = result.scalars().all()
    
    return fragments

@router.post("/", response_model=FragmentSchema)
async def create_fragment(
    video_id: int,
    fragment: FragmentCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if fragment.start_time < 0 or fragment.end_time > video.duration:
        raise HTTPException(
            status_code=400,
            detail="Fragment time range is outside video duration"
        )
    
    if fragment.start_time >= fragment.end_time:
        raise HTTPException(
            status_code=400,
            detail="Start time must be less than end time"
        )
    
    fragment_obj = Fragment(
        video_id=video_id,
        name=fragment.name,
        description=fragment.description,
        start_time=fragment.start_time,
        end_time=fragment.end_time
    )
    
    if fragment.tag_ids:
        for tag_id in fragment.tag_ids:
            result = await db.execute(select(Tag).where(Tag.id == tag_id))
            tag = result.scalar_one_or_none()
            if tag:
                fragment_obj.tags.append(tag)
    
    db.add(fragment_obj)
    await db.commit()
    await db.refresh(fragment_obj)
    
    # Проверяем что исходное видео существует
    if not video.filepath or not os.path.exists(video.filepath):
        await db.delete(fragment_obj)
        await db.commit()
        raise HTTPException(status_code=400, detail="Source video file not found. Cannot create fragment without source video.")
    
    fragment_filename = f"fragment_{fragment_obj.id}_{video.filename}"
    fragment_path = Path(settings.FRAGMENTS_DIR) / fragment_filename
    
    try:
        output_path = await ffmpeg_service.extract_fragment(
            video.filepath,
            str(fragment_path),
            fragment.start_time,
            fragment.end_time
        )
        
        # Сохраняем путь относительно static директории (uploads)
        # fragments/filename
        fragment_obj.video_filepath = f"fragments/{fragment_filename}"
        if os.path.exists(output_path):
            fragment_obj.video_file_size = os.path.getsize(output_path)
        
        await db.commit()
    except Exception as e:
        await db.delete(fragment_obj)
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to extract fragment: {str(e)}")
    
    return fragment_obj

@router.get("/", response_model=List[FragmentWithTags])
async def get_fragments(
    video_id: int,
    query: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Fragment)
        .options(selectinload(Fragment.tags), selectinload(Fragment.video))
        .where(Fragment.video_id == video_id)
    )
    
    if query:
        stmt = stmt.where(
            or_(
                Fragment.name.ilike(f"%{query}%"),
                Fragment.description.ilike(f"%{query}%")
            )
        )
    
    result = await db.execute(stmt)
    fragments = result.scalars().all()
    
    return fragments

@router.get("/{fragment_id}", response_model=FragmentWithTags)
async def get_fragment(
    video_id: int,
    fragment_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Fragment)
        .options(selectinload(Fragment.tags), selectinload(Fragment.video))
        .where(
            and_(Fragment.id == fragment_id, Fragment.video_id == video_id)
        )
    )
    fragment = result.scalar_one_or_none()
    
    if not fragment:
        raise HTTPException(status_code=404, detail="Fragment not found")
    
    return fragment

@router.put("/{fragment_id}", response_model=FragmentSchema)
async def update_fragment(
    video_id: int,
    fragment_id: int,
    fragment_update: FragmentUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Fragment).where(
            and_(Fragment.id == fragment_id, Fragment.video_id == video_id)
        )
    )
    fragment = result.scalar_one_or_none()
    
    if not fragment:
        raise HTTPException(status_code=404, detail="Fragment not found")
    
    update_data = fragment_update.model_dump(exclude_unset=True)
    
    if "tag_ids" in update_data:
        fragment.tags.clear()
        for tag_id in update_data["tag_ids"] or []:
            result = await db.execute(select(Tag).where(Tag.id == tag_id))
            tag = result.scalar_one_or_none()
            if tag:
                fragment.tags.append(tag)
        del update_data["tag_ids"]
    
    for key, value in update_data.items():
        setattr(fragment, key, value)
    
    await db.commit()
    await db.refresh(fragment)
    
    return fragment

@router.delete("/{fragment_id}")
async def delete_fragment(
    video_id: int,
    fragment_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Fragment).where(
            and_(Fragment.id == fragment_id, Fragment.video_id == video_id)
        )
    )
    fragment = result.scalar_one_or_none()
    
    if not fragment:
        raise HTTPException(status_code=404, detail="Fragment not found")
    
    # Удаляем видеофайл фрагмента
    if fragment.video_filepath and os.path.exists(fragment.video_filepath):
        os.remove(fragment.video_filepath)
    
    # Удаляем превью/скриншот если есть
    if fragment.filepath and os.path.exists(fragment.filepath):
        os.remove(fragment.filepath)
    
    await db.delete(fragment)
    await db.commit()
    
    return {"message": "Fragment deleted successfully"}

from sqlalchemy import and_
