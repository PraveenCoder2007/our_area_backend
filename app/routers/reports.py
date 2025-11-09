from fastapi import APIRouter, Depends, HTTPException
from ..models.schemas import ReportCreate, APIResponse
from ..core.auth import get_current_user
from ..core.database import get_database
import uuid

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("", response_model=APIResponse)
async def create_report(
    report_data: ReportCreate,
    current_user: dict = Depends(get_current_user)
):
    db = await get_database()
    
    # Validate that either post_id or user_id is provided
    if not report_data.post_id and not report_data.user_id:
        raise HTTPException(status_code=400, detail="Either post_id or user_id must be provided")
    
    # Validate post exists if post_id provided
    if report_data.post_id:
        post = await db.fetch_one(
            "SELECT id FROM posts WHERE id = :post_id AND is_deleted = 0",
            {"post_id": report_data.post_id}
        )
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
    
    # Validate user exists if user_id provided
    if report_data.user_id:
        user = await db.fetch_one(
            "SELECT id FROM users WHERE id = :user_id",
            {"user_id": report_data.user_id}
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    
    # Create report
    report_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO reports (id, reporter_id, post_id, user_id, reason, description)
           VALUES (:id, :reporter_id, :post_id, :user_id, :reason, :description)""",
        {
            "id": report_id,
            "reporter_id": current_user["id"],
            "post_id": report_data.post_id,
            "user_id": report_data.user_id,
            "reason": report_data.reason.value,
            "description": report_data.description
        }
    )
    
    return APIResponse(status="success", message="Report submitted successfully", data={"report_id": report_id})