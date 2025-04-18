# exam_time.py
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone, timedelta
from typing import Optional
from pydantic import BaseModel

from models.user import User
from database import SessionLocal
from routers.auth import get_current_user
from utils.cache import invalidate_cache

router = APIRouter()


class ExamTimeResponse(BaseModel):
    time_start: Optional[datetime] = None
    duration: Optional[int] = None
    time_end: Optional[datetime] = None
    remaining_seconds: Optional[int] = None
    is_active: bool = False


class StartExamRequest(BaseModel):
    duration: Optional[int] = 3600  # Default: 60 minutes (in seconds)


@router.post("/start", response_model=ExamTimeResponse)
async def start_exam(
    request: StartExamRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Bắt đầu thời gian làm bài thi cho người dùng hiện tại.
    
    Parameters:
        request: Thông tin về thời lượng bài thi
        current_user: Người dùng hiện tại
        
    Returns:
        Thông tin về thời gian bài thi
    """
    db = SessionLocal()
    try:
        # Kiểm tra xem người dùng đã có bài thi đang diễn ra không
        if current_user.time_start and current_user.time_end:
            now = datetime.now(timezone.utc)
            if now < current_user.time_end:
                # Bài thi đang diễn ra
                remaining_seconds = int((current_user.time_end - now).total_seconds())
                return ExamTimeResponse(
                    time_start=current_user.time_start,
                    duration=current_user.duration,
                    time_end=current_user.time_end,
                    remaining_seconds=remaining_seconds,
                    is_active=True
                )
        
        # Bắt đầu bài thi mới
        now = datetime.now(timezone.utc)
        duration = request.duration or 3600
        time_end = now + timedelta(seconds=duration)
        
        # Cập nhật thông tin người dùng
        current_user.time_start = now
        current_user.duration = duration
        current_user.time_end = time_end
        
        db.add(current_user)
        db.commit()
        
        # Xóa cache
        await invalidate_cache(f"get_profile:*:{current_user.email}*")
        
        return ExamTimeResponse(
            time_start=now,
            duration=duration,
            time_end=time_end,
            remaining_seconds=duration,
            is_active=True
        )
    finally:
        db.close()


@router.get("/status", response_model=ExamTimeResponse)
async def get_exam_status(current_user: User = Depends(get_current_user)):
    """
    Lấy thông tin về trạng thái thời gian bài thi của người dùng hiện tại.
    
    Parameters:
        current_user: Người dùng hiện tại
        
    Returns:
        Thông tin về thời gian bài thi
    """
    # Kiểm tra xem người dùng có bài thi đang diễn ra không
    if current_user.time_start and current_user.time_end:
        now = datetime.now(timezone.utc)
        if now < current_user.time_end:
            # Bài thi đang diễn ra
            remaining_seconds = int((current_user.time_end - now).total_seconds())
            return ExamTimeResponse(
                time_start=current_user.time_start,
                duration=current_user.duration,
                time_end=current_user.time_end,
                remaining_seconds=remaining_seconds,
                is_active=True
            )
    
    # Không có bài thi đang diễn ra
    return ExamTimeResponse(
        time_start=current_user.time_start,
        duration=current_user.duration,
        time_end=current_user.time_end,
        remaining_seconds=0,
        is_active=False
    )


@router.post("/end", response_model=ExamTimeResponse)
async def end_exam(current_user: User = Depends(get_current_user)):
    """
    Kết thúc bài thi của người dùng hiện tại.
    
    Parameters:
        current_user: Người dùng hiện tại
        
    Returns:
        Thông tin về thời gian bài thi
    """
    db = SessionLocal()
    try:
        # Kiểm tra xem người dùng có bài thi đang diễn ra không
        if not (current_user.time_start and current_user.time_end):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không có bài thi đang diễn ra"
            )
        
        now = datetime.now(timezone.utc)
        if now >= current_user.time_end:
            # Bài thi đã kết thúc
            return ExamTimeResponse(
                time_start=current_user.time_start,
                duration=current_user.duration,
                time_end=current_user.time_end,
                remaining_seconds=0,
                is_active=False
            )
        
        # Kết thúc bài thi sớm
        current_user.time_end = now
        
        db.add(current_user)
        db.commit()
        
        # Xóa cache
        await invalidate_cache(f"get_profile:*:{current_user.email}*")
        
        return ExamTimeResponse(
            time_start=current_user.time_start,
            duration=current_user.duration,
            time_end=now,
            remaining_seconds=0,
            is_active=False
        )
    finally:
        db.close()


@router.post("/reset", response_model=ExamTimeResponse)
async def reset_exam_time(current_user: User = Depends(get_current_user)):
    """
    Đặt lại thời gian bài thi của người dùng hiện tại.
    
    Parameters:
        current_user: Người dùng hiện tại
        
    Returns:
        Thông tin về thời gian bài thi
    """
    db = SessionLocal()
    try:
        # Đặt lại thời gian bài thi
        current_user.time_start = None
        current_user.time_end = None
        
        db.add(current_user)
        db.commit()
        
        # Xóa cache
        await invalidate_cache(f"get_profile:*:{current_user.email}*")
        
        return ExamTimeResponse(
            time_start=None,
            duration=current_user.duration,
            time_end=None,
            remaining_seconds=0,
            is_active=False
        )
    finally:
        db.close()
