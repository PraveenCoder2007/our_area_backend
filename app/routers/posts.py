from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..models.schemas import PostCreate, PostUpdate, PostResponse, CommentCreate, CommentUpdate, CommentResponse, APIResponse
from ..core.auth import get_current_user
from ..core.database import get_database
import uuid

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("/feed", response_model=List[PostResponse])
async def get_feed(
    area_id: str = Query(...),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    db = await get_database()
    offset = (page - 1) * limit
    
    # Get posts with user info, likes, and comments count
    query = """
        SELECT p.*, u.display_name, u.username, u.avatar_url,
               COUNT(DISTINCT l.id) as likes_count,
               COUNT(DISTINCT c.id) as comments_count,
               CASE WHEN ul.id IS NOT NULL THEN 1 ELSE 0 END as is_liked,
               CASE WHEN uw.id IS NOT NULL THEN 1 ELSE 0 END as is_wishlisted
        FROM posts p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN likes l ON p.id = l.post_id
        LEFT JOIN comments c ON p.id = c.post_id
        LEFT JOIN likes ul ON p.id = ul.post_id AND ul.user_id = :current_user_id
        LEFT JOIN wishlists uw ON p.id = uw.post_id AND uw.user_id = :current_user_id
        WHERE p.area_id = :area_id AND p.is_deleted = 0
        GROUP BY p.id
        ORDER BY p.created_at DESC
        LIMIT :limit OFFSET :offset
    """
    
    posts = await db.fetch_all(query, {
        "area_id": area_id,
        "current_user_id": current_user["id"],
        "limit": limit,
        "offset": offset
    })
    
    result = []
    for post in posts:
        # Get post images
        images = await db.fetch_all(
            "SELECT * FROM post_images WHERE post_id = :post_id ORDER BY order_idx",
            {"post_id": post["id"]}
        )
        
        result.append(PostResponse(
            id=post["id"],
            user_id=post["user_id"],
            area_id=post["area_id"],
            text=post["text"],
            category=post["category"],
            lat=post["lat"],
            lng=post["lng"],
            event_time=post["event_time"],
            created_at=post["created_at"],
            updated_at=post["updated_at"],
            images=[{
                "id": img["id"],
                "url": img["url"],
                "order_idx": img["order_idx"]
            } for img in images],
            likes_count=post["likes_count"],
            comments_count=post["comments_count"],
            is_liked=bool(post["is_liked"]),
            is_wishlisted=bool(post["is_wishlisted"]),
            user={
                "display_name": post["display_name"],
                "username": post["username"],
                "avatar_url": post["avatar_url"]
            }
        ))
    
    return result

@router.post("", response_model=APIResponse)
async def create_post(
    post_data: PostCreate,
    current_user: dict = Depends(get_current_user)
):
    db = await get_database()
    
    # User must have an area_id to post
    if not current_user.get("area_id"):
        raise HTTPException(status_code=400, detail="User must be assigned to an area to post")
    
    post_id = str(uuid.uuid4())
    
    # Create post
    await db.execute(
        """INSERT INTO posts (id, user_id, area_id, location_id, text, category, lat, lng, event_time)
           VALUES (:id, :user_id, :area_id, :location_id, :text, :category, :lat, :lng, :event_time)""",
        {
            "id": post_id,
            "user_id": current_user["id"],
            "area_id": current_user["area_id"],
            "location_id": post_data.location_id,
            "text": post_data.text,
            "category": post_data.category.value,
            "lat": post_data.lat,
            "lng": post_data.lng,
            "event_time": post_data.event_time
        }
    )
    
    # Add images if provided
    if post_data.images:
        for idx, image_url in enumerate(post_data.images):
            await db.execute(
                "INSERT INTO post_images (id, post_id, url, order_idx) VALUES (:id, :post_id, :url, :order_idx)",
                {
                    "id": str(uuid.uuid4()),
                    "post_id": post_id,
                    "url": image_url,
                    "order_idx": idx
                }
            )
    
    return APIResponse(status="success", message="Post created successfully", data={"post_id": post_id})

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    query = """
        SELECT p.*, u.display_name, u.username, u.avatar_url,
               COUNT(DISTINCT l.id) as likes_count,
               COUNT(DISTINCT c.id) as comments_count,
               CASE WHEN ul.id IS NOT NULL THEN 1 ELSE 0 END as is_liked,
               CASE WHEN uw.id IS NOT NULL THEN 1 ELSE 0 END as is_wishlisted
        FROM posts p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN likes l ON p.id = l.post_id
        LEFT JOIN comments c ON p.id = c.post_id
        LEFT JOIN likes ul ON p.id = ul.post_id AND ul.user_id = :current_user_id
        LEFT JOIN wishlists uw ON p.id = uw.post_id AND uw.user_id = :current_user_id
        WHERE p.id = :post_id AND p.is_deleted = 0
        GROUP BY p.id
    """
    
    post = await db.fetch_one(query, {"post_id": post_id, "current_user_id": current_user["id"]})
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Get images
    images = await db.fetch_all(
        "SELECT * FROM post_images WHERE post_id = :post_id ORDER BY order_idx",
        {"post_id": post_id}
    )
    
    return PostResponse(
        id=post["id"],
        user_id=post["user_id"],
        area_id=post["area_id"],
        text=post["text"],
        category=post["category"],
        lat=post["lat"],
        lng=post["lng"],
        event_time=post["event_time"],
        created_at=post["created_at"],
        updated_at=post["updated_at"],
        images=[{
            "id": img["id"],
            "url": img["url"],
            "order_idx": img["order_idx"]
        } for img in images],
        likes_count=post["likes_count"],
        comments_count=post["comments_count"],
        is_liked=bool(post["is_liked"]),
        is_wishlisted=bool(post["is_wishlisted"]),
        user={
            "display_name": post["display_name"],
            "username": post["username"],
            "avatar_url": post["avatar_url"]
        }
    )

@router.post("/{post_id}/like", response_model=APIResponse)
async def toggle_like(post_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    # Check if already liked
    existing_like = await db.fetch_one(
        "SELECT id FROM likes WHERE post_id = :post_id AND user_id = :user_id",
        {"post_id": post_id, "user_id": current_user["id"]}
    )
    
    if existing_like:
        # Remove like
        await db.execute(
            "DELETE FROM likes WHERE post_id = :post_id AND user_id = :user_id",
            {"post_id": post_id, "user_id": current_user["id"]}
        )
        return APIResponse(status="success", message="Like removed")
    else:
        # Add like
        await db.execute(
            "INSERT INTO likes (id, post_id, user_id) VALUES (:id, :post_id, :user_id)",
            {"id": str(uuid.uuid4()), "post_id": post_id, "user_id": current_user["id"]}
        )
        return APIResponse(status="success", message="Post liked")

@router.post("/{post_id}/wishlist", response_model=APIResponse)
async def toggle_wishlist(post_id: str, current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    # Check if already wishlisted
    existing_wishlist = await db.fetch_one(
        "SELECT id FROM wishlists WHERE post_id = :post_id AND user_id = :user_id",
        {"post_id": post_id, "user_id": current_user["id"]}
    )
    
    if existing_wishlist:
        # Remove from wishlist
        await db.execute(
            "DELETE FROM wishlists WHERE post_id = :post_id AND user_id = :user_id",
            {"post_id": post_id, "user_id": current_user["id"]}
        )
        return APIResponse(status="success", message="Removed from wishlist")
    else:
        # Add to wishlist
        await db.execute(
            "INSERT INTO wishlists (id, post_id, user_id) VALUES (:id, :post_id, :user_id)",
            {"id": str(uuid.uuid4()), "post_id": post_id, "user_id": current_user["id"]}
        )
        return APIResponse(status="success", message="Added to wishlist")

@router.get("/{post_id}/comments", response_model=List[CommentResponse])
async def get_comments(post_id: str):
    db = await get_database()
    
    comments = await db.fetch_all(
        """SELECT c.*, u.display_name, u.username, u.avatar_url
           FROM comments c
           JOIN users u ON c.user_id = u.id
           WHERE c.post_id = :post_id
           ORDER BY c.created_at ASC""",
        {"post_id": post_id}
    )
    
    return [CommentResponse(
        id=comment["id"],
        post_id=comment["post_id"],
        user_id=comment["user_id"],
        text=comment["text"],
        created_at=comment["created_at"],
        user={
            "display_name": comment["display_name"],
            "username": comment["username"],
            "avatar_url": comment["avatar_url"]
        }
    ) for comment in comments]

@router.post("/{post_id}/comments", response_model=APIResponse)
async def add_comment(
    post_id: str,
    comment_data: CommentCreate,
    current_user: dict = Depends(get_current_user)
):
    db = await get_database()
    
    # Verify post exists
    post = await db.fetch_one("SELECT id FROM posts WHERE id = :post_id AND is_deleted = 0", {"post_id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comment_id = str(uuid.uuid4())
    await db.execute(
        "INSERT INTO comments (id, post_id, user_id, text) VALUES (:id, :post_id, :user_id, :text)",
        {
            "id": comment_id,
            "post_id": post_id,
            "user_id": current_user["id"],
            "text": comment_data.text
        }
    )
    
    return APIResponse(status="success", message="Comment added successfully", data={"comment_id": comment_id})

@router.put("/{post_id}", response_model=APIResponse)
async def update_post(
    post_id: str,
    post_update: PostUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = await get_database()
    
    # Check if post exists and user owns it
    post = await db.fetch_one(
        "SELECT user_id FROM posts WHERE id = :post_id AND is_deleted = 0",
        {"post_id": post_id}
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    
    # Build update query
    update_fields = []
    values = {"post_id": post_id}
    
    for field, value in post_update.dict(exclude_unset=True).items():
        if field == "category" and value:
            update_fields.append(f"{field} = :{field}")
            values[field] = value.value
        elif value is not None:
            update_fields.append(f"{field} = :{field}")
            values[field] = value
    
    if not update_fields:
        return APIResponse(status="success", message="No changes to update")
    
    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    query = f"UPDATE posts SET {', '.join(update_fields)} WHERE id = :post_id"
    await db.execute(query, values)
    
    return APIResponse(status="success", message="Post updated successfully")

@router.put("/{post_id}/comments/{comment_id}", response_model=APIResponse)
async def update_comment(
    post_id: str,
    comment_id: str,
    comment_update: CommentUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = await get_database()
    
    # Check if comment exists and user owns it
    comment = await db.fetch_one(
        "SELECT user_id FROM comments WHERE id = :comment_id AND post_id = :post_id",
        {"comment_id": comment_id, "post_id": post_id}
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")
    
    await db.execute(
        "UPDATE comments SET text = :text WHERE id = :comment_id",
        {"text": comment_update.text, "comment_id": comment_id}
    )
    
    return APIResponse(status="success", message="Comment updated successfully")