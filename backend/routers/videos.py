from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
import aiofiles
import os
import magic
from datetime import datetime
from pathlib import Path
import uuid
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from config import settings
from models import Video, Tag, video_tags, Fragment
from schemas import VideoCreate, VideoUpdate, Video as VideoSchema, VideoWithTags, SearchQuery
from services.ffmpeg_service import ffmpeg_service
from services.yandex_disk import YandexDiskService
from database import get_db
from routers.auth import get_current_active_user, get_current_user

router = APIRouter(prefix="/videos", tags=["videos"])

@router.post("/upload", response_model=VideoSchema)
async def upload_video(
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    subcategory: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    content_type = file.content_type or ""
    filename = file.filename or ""
    logger.debug(f"Uploading file: {filename}, content_type: {content_type}")
    
    if not (content_type.startswith("video/") or filename.endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv'))):
        logger.error(f"Invalid file type: {content_type}, filename: {filename}")
        raise HTTPException(status_code=400, detail=f"File must be a video. Got: {content_type}")
    
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    upload_path = Path(settings.UPLOAD_DIR) / unique_filename
    
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    
    async with aiofiles.open(upload_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    file_size = len(content)
    logger.debug(f"File saved, size: {file_size}")
    
    try:
        logger.debug("Getting video info with FFmpeg...")
        video_info = await ffmpeg_service.get_video_info(str(upload_path))
        logger.debug(f"Video info: {video_info}")
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"FFmpeg error: {str(e)}")
        logger.error(f"Traceback: {error_trace}")
        os.remove(upload_path)
        raise HTTPException(status_code=400, detail=f"FFmpeg error: {str(e)}")
    
    video = Video(
        filename=unique_filename,
        original_filename=file.filename,
        title=title or file.filename,
        filepath=str(upload_path),
        file_size=file_size,
        mime_type=content_type,
        duration=video_info['duration'],
        category=category,
        subcategory=subcategory
    )
    
    if tags:
        tag_list = [tag.strip().lower() for tag in tags.split(",")]
        for tag_name in tag_list:
            existing_tag = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag_obj = existing_tag.scalar_one_or_none()
            if not tag_obj:
                tag_obj = Tag(name=tag_name)
                db.add(tag_obj)
                await db.flush()
            video.tags.append(tag_obj)
    
    db.add(video)
    await db.commit()
    await db.refresh(video)
    
    try:
        thumbnail_dir = Path(settings.UPLOAD_DIR) / "thumbnails"
        thumbnail_dir.mkdir(parents=True, exist_ok=True)
        thumbnail_path = thumbnail_dir / f"{video.id}.jpg"
        logger.debug(f"Generating thumbnail at: {thumbnail_path}")
        await ffmpeg_service.generate_thumbnail(str(upload_path), str(thumbnail_path))
        logger.debug("Thumbnail generated successfully")
    except Exception as e:
        logger.error(f"Thumbnail generation error: {str(e)}")
        # Don't fail if thumbnail generation fails
        pass
    
    # Конвертируем AVI в MP4 для лучшей совместимости с браузерами
    if file.filename.lower().endswith('.avi'):
        try:
            mp4_filename = unique_filename.replace('.avi', '.mp4')
            mp4_path = os.path.join(settings.UPLOAD_DIR, mp4_filename)
            
            logger.debug(f"Converting AVI to MP4: {upload_path} -> {mp4_path}")
            
            cmd = [
                settings.FFMPEG_PATH,
                "-y",
                "-i", str(upload_path),
                "-c:v", "libx264",
                "-c:a", "aac", 
                "-preset", "medium",
                mp4_path
            ]
            
            process = await asyncio.create_subprocess_exec(*cmd)
            await process.wait()
            
            if process.returncode == 0:
                # Обновляем запись в базе данных
                video.filepath = f"static/uploads/{mp4_filename}"
                video.filename = mp4_filename
                video.mime_type = "video/mp4"
                await db.commit()
                logger.debug(f"Successfully converted to MP4: {mp4_filename}")
                
                # Удаляем исходный AVI файл
                os.remove(upload_path)
                logger.debug(f"Removed original AVI file: {upload_path}")
            else:
                logger.error("MP4 conversion failed")
        except Exception as e:
            logger.error(f"AVI to MP4 conversion error: {str(e)}")
            # Don't fail upload if conversion fails
    
    return video

@router.get("/", response_model=List[VideoSchema])
async def get_videos(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Video)
    
    if category:
        query = query.where(Video.category == category)
    if subcategory:
        query = query.where(Video.subcategory == subcategory)
    
    query = query.offset(skip).limit(limit).order_by(Video.created_at.desc())
    
    result = await db.execute(query)
    videos = result.scalars().all()
    
    return videos

@router.get("/{video_id}", response_model=VideoWithTags)
async def get_video(video_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Video)
        .options(selectinload(Video.tags), selectinload(Video.fragments))
        .where(Video.id == video_id)
    )
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return video

@router.put("/{video_id}", response_model=VideoSchema)
async def update_video(
    video_id: int,
    video_update: VideoUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    update_data = video_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(video, key, value)
    
    video.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(video)
    
    return video

@router.delete("/{video_id}")
async def delete_video(video_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Video)
        .options(selectinload(Video.fragments))
        .where(Video.id == video_id)
    )
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Delete source video file if exists
    if video.filepath and os.path.exists(video.filepath):
        try:
            os.remove(video.filepath)
        except Exception as e:
            logger.warning(f"Could not delete video file: {e}")
    
    # Delete thumbnail if exists
    thumbnail_path = Path(settings.UPLOAD_DIR) / f"thumbnails/{video.id}.jpg"
    if thumbnail_path.exists():
        try:
            thumbnail_path.unlink()
        except Exception as e:
            logger.warning(f"Could not delete thumbnail: {e}")
    
    # Delete fragment video files
    if video.fragments:
        for fragment in video.fragments:
            if fragment.video_filepath:
                fragment_path = Path(settings.UPLOAD_DIR) / fragment.video_filepath.replace("uploads/", "")
                if fragment_path.exists():
                    try:
                        fragment_path.unlink()
                    except Exception as e:
                        logger.warning(f"Could not delete fragment file {fragment_path}: {e}")
    
    await db.delete(video)
    await db.commit()
    
    return {"message": "Video deleted successfully"}

@router.delete("/{video_id}/source")
async def delete_source_video(
    video_id: int, 
    force: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Delete only the source video file, keeping the record and fragments in archive"""
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if not video.filepath:
        return {"message": "No source file to delete"}
    
    file_deleted = False
    
    try:
        if os.path.exists(video.filepath):
            if force:
                # Force mode: try multiple times with delays
                for attempt in range(5):
                    try:
                        os.remove(video.filepath)
                        file_deleted = True
                        break
                    except PermissionError:
                        if attempt < 4:  # Not the last attempt
                            logger.info(f"Attempt {attempt + 1} failed, retrying in 1 second...")
                            import asyncio
                            await asyncio.sleep(1)
                        else:
                            logger.warning(f"Could not delete file after 5 attempts, marking as deleted in database")
                            # Rename file to mark it for deletion
                            try:
                                temp_path = video.filepath + ".deleted"
                                os.rename(video.filepath, temp_path)
                                file_deleted = True
                            except:
                                pass
            else:
                # Normal mode: single attempt
                os.remove(video.filepath)
                file_deleted = True
        else:
            file_deleted = True  # File already doesn't exist
        
        # Update database regardless of file deletion success
        video.filepath = None
        video.file_size = 0
        video.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(video)
        
        if file_deleted:
            return {"message": "Source video file deleted. Video record and fragments kept in archive."}
        else:
            return {"message": "Video marked as deleted in database. File will be removed when no longer in use."}
    
    except PermissionError:
        raise HTTPException(
            status_code=409, 
            detail="The file is currently in use by another process. Use force=true parameter or close the video player and try again."
        )
    
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete the file")

@router.post("/search", response_model=List[VideoWithTags])
async def search_videos(search: SearchQuery, db: AsyncSession = Depends(get_db)):
    query = select(Video).options(selectinload(Video.tags), selectinload(Video.fragments))
    
    conditions = []
    
    if search.query:
        conditions.append(or_(
            Video.title.ilike(f"%{search.query}%"),
            Video.original_filename.ilike(f"%{search.query}%")
        ))
    
    if search.category:
        conditions.append(Video.category == search.category)
    
    if search.subcategory:
        conditions.append(Video.subcategory == search.subcategory)
    
    if search.date_from:
        conditions.append(Video.created_at >= search.date_from)
    
    if search.date_to:
        conditions.append(Video.created_at <= search.date_to)
    
    if search.tags:
        query = query.join(video_tags).join(Tag)
        conditions.append(Tag.name.in_(search.tags))
    
    if conditions:
        query = query.where(and_(*conditions))
    
    result = await db.execute(query.order_by(Video.created_at.desc()))
    videos = result.scalars().unique().all()
    
    return videos
