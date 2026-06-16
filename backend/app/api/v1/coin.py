"""
Coin API - API endpoints cho các thao tác liên quan đến coin.
"""
from __future__ import annotations
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user_id, DBSession
from app.services.coin import CoinService
from app.schemas.coin import (
    CoinBalanceResponse,
    CoinTransactionListResponse,
    PurchaseCoinRequest,
    PurchaseCoinResponse,
    PurchaseCourseWithCoinRequest,
    PurchaseCourseWithCoinResponse,
    RefundCourseRequest,
    RefundCourseResponse,
    CourseCoinPrice,
    CoinPackageRead
)

router = APIRouter(prefix="/coin", tags=["Coin"])


def get_coin_service(db: DBSession) -> CoinService:
    """Dependency injection cho CoinService."""
    return CoinService(db)


# ─── Coin Balance ──────────────────────────────────────────────────────────────

@router.get("/balance", response_model=CoinBalanceResponse)
async def get_my_coin_balance(
    db: DBSession,
    current_user_id: UUID = Depends(get_current_user_id),
):
    """Lấy số dư coin của user hiện tại."""
    coin_service = get_coin_service(db)
    return await coin_service.get_balance(current_user_id)


# ─── Coin Transactions ─────────────────────────────────────────────────────────

@router.get("/transactions", response_model=CoinTransactionListResponse)
async def get_my_transactions(
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tx_type: Optional[str] = Query(None, description="Lọc theo loại giao dịch: PURCHASE, COURSE_PURCHASE, REFUND, BONUS"),
    current_user_id: UUID = Depends(get_current_user_id),
):
    """Lấy lịch sử giao dịch coin của user hiện tại."""
    coin_service = get_coin_service(db)
    return await coin_service.get_transactions(
        user_id=current_user_id,
        page=page,
        page_size=page_size,
        tx_type=tx_type
    )


# ─── Purchase Coin ─────────────────────────────────────────────────────────────

@router.post("/purchase", response_model=PurchaseCoinResponse)
async def create_coin_purchase_order(
    db: DBSession,
    request: PurchaseCoinRequest,
    current_user_id: UUID = Depends(get_current_user_id),
):
    """
    Tạo order mua coin.
    
    Sau khi tạo order thành công, frontend sẽ redirect user đến payment_url
    để thanh toán. Sau khi thanh toán thành công, gọi POST /coin/purchase/confirm
    để xác nhận và cộng coin.
    """
    try:
        coin_service = get_coin_service(db)
        return await coin_service.create_purchase_order(
            user_id=current_user_id,
            request=request
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/purchase/confirm", response_model=CoinBalanceResponse)
async def confirm_coin_purchase(
    db: DBSession,
    order_id: str,
    coin_amount: int,
    bonus_coin: int = 0,
    current_user_id: UUID = Depends(get_current_user_id),
):
    """
    Xác nhận thanh toán và cộng coin.
    
    Endpoint này được gọi từ payment gateway callback sau khi thanh toán thành công.
    Trong thực tế, nên verify signature từ payment gateway.
    """
    coin_service = get_coin_service(db)
    return await coin_service.confirm_coin_purchase(
        user_id=current_user_id,
        order_id=order_id,
        amount=coin_amount,
        bonus_coin=bonus_coin
    )


# ─── Purchase Course with Coin ─────────────────────────────────────────────────

@router.get("/course/{course_id}/price", response_model=CourseCoinPrice)
async def get_course_coin_price(
    db: DBSession,
    course_id: UUID,
):
    """Lấy giá coin của một khóa học."""
    from sqlalchemy import select
    from app.models.database import Courses
    
    result = await db.execute(
        select(Courses).where(Courses.id == course_id)
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Khóa học không tồn tại")
    
    price_coin = course.base_price // 1000
    if course.base_price % 1000 > 0:
        price_coin += 1
    
    return CourseCoinPrice(
        course_id=course_id,
        price_vnd=course.base_price,
        price_coin=price_coin,
        has_discount=False,
        discount_percent=0,
        final_price_coin=price_coin
    )


@router.post("/course/purchase", response_model=PurchaseCourseWithCoinResponse)
async def purchase_course_with_coin(
    db: DBSession,
    request: PurchaseCourseWithCoinRequest,
    current_user_id: UUID = Depends(get_current_user_id),
):
    """
    Mua khóa học bằng coin.
    
    User phải có đủ số dư coin để mua khóa học.
    """
    coin_service = get_coin_service(db)
    return await coin_service.purchase_course_with_coin(
        user_id=current_user_id,
        course_id=request.course_id
    )


@router.post("/course/refund", response_model=RefundCourseResponse)
async def refund_course_coin(
    db: DBSession,
    request: RefundCourseRequest,
    current_user_id: UUID = Depends(get_current_user_id),
):
    """
    Yêu cầu hoàn coin khi hủy khóa học.
    
    Chỉ áp dụng cho các khóa học đã mua bằng coin.
    """
    coin_service = get_coin_service(db)
    return await coin_service.refund_course_coin(
        user_id=current_user_id,
        request=request
    )


# ─── Coin Packages (Public) ────────────────────────────────────────────────────

@router.get("/packages", response_model=list[CoinPackageRead])
async def get_coin_packages():
    """Lấy danh sách các gói coin có thể mua."""
    return [
        CoinPackageRead(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            name="Starter",
            coin_amount=100,
            price_vnd=100000,
            bonus_coin=0,
            is_active=True
        ),
        CoinPackageRead(
            id=UUID("00000000-0000-0000-0000-000000000002"),
            name="Pro",
            coin_amount=500,
            price_vnd=450000,
            bonus_coin=50,
            is_active=True
        ),
        CoinPackageRead(
            id=UUID("00000000-0000-0000-0000-000000000003"),
            name="Premium",
            coin_amount=1000,
            price_vnd=850000,
            bonus_coin=150,
            is_active=True
        ),
    ]
