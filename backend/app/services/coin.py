"""
Coin Service - Xử lý các thao tác liên quan đến coin.
"""
from __future__ import annotations
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime
import uuid

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import (
    UserCoins, CoinTransactions, CoinTransactionType, 
    Users, Courses
)
from app.schemas.coin import (
    CoinBalanceResponse, CoinTransactionRead, CoinTransactionListResponse,
    PurchaseCoinRequest, PurchaseCoinResponse,
    PurchaseCourseWithCoinRequest, PurchaseCourseWithCoinResponse,
    RefundCourseRequest, RefundCourseResponse,
    AdminAddCoinRequest, AdminCoinOperationResponse,
    CoinPackageRead
)

# Tỷ lệ quy đổi: 1 coin = 1000 VND
COIN_CONVERSION_RATE = 1000


class CoinService:
    """Service xử lý coin operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ─── Coin Balance ────────────────────────────────────────────────────────────

    async def get_balance(self, user_id: UUID) -> CoinBalanceResponse:
        """Lấy số dư coin của user."""
        result = await self.db.execute(
            select(UserCoins).where(UserCoins.user_id == user_id)
        )
        user_coin = result.scalar_one_or_none()

        if not user_coin:
            # Tạo tài khoản coin mới nếu chưa có
            user_coin = UserCoins(
                user_id=user_id,
                balance=0,
                total_purchased=0,
                total_spent=0
            )
            self.db.add(user_coin)
            await self.db.commit()
            await self.db.refresh(user_coin)

        return CoinBalanceResponse(
            balance=user_coin.balance,
            total_purchased=user_coin.total_purchased,
            total_spent=user_coin.total_spent,
            conversion_rate=COIN_CONVERSION_RATE
        )

    async def get_or_create_account(self, user_id: UUID) -> UserCoins:
        """Lấy hoặc tạo tài khoản coin cho user."""
        result = await self.db.execute(
            select(UserCoins).where(UserCoins.user_id == user_id)
        )
        user_coin = result.scalar_one_or_none()

        if not user_coin:
            user_coin = UserCoins(
                user_id=user_id,
                balance=0,
                total_purchased=0,
                total_spent=0
            )
            self.db.add(user_coin)
            await self.db.commit()
            await self.db.refresh(user_coin)

        return user_coin

    # ─── Coin Transactions ──────────────────────────────────────────────────────

    async def get_transactions(
        self, 
        user_id: UUID, 
        page: int = 1, 
        page_size: int = 20,
        tx_type: Optional[str] = None
    ) -> CoinTransactionListResponse:
        """Lấy lịch sử giao dịch coin của user."""
        # Build query
        query = select(CoinTransactions).where(
            CoinTransactions.user_id == user_id
        )
        
        if tx_type:
            query = query.where(CoinTransactions.type == tx_type)
        
        # Count total
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.order_by(desc(CoinTransactions.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        transactions = result.scalars().all()

        return CoinTransactionListResponse(
            transactions=[
                CoinTransactionRead(
                    id=tx.id,
                    type=tx.type.value if hasattr(tx.type, 'value') else tx.type,
                    amount=tx.amount,
                    balance_after=tx.balance_after,
                    description=tx.description,
                    metadata=tx.extra_data or {},
                    created_at=tx.created_at
                )
                for tx in transactions
            ],
            total=total,
            page=page,
            page_size=page_size
        )

    # ─── Add/Deduct Coin ───────────────────────────────────────────────────────

    async def add_coin(
        self,
        user_id: UUID,
        amount: int,
        tx_type: CoinTransactionType,
        description: str,
        metadata: Optional[dict] = None
    ) -> Tuple[UserCoins, CoinTransactions]:
        """
        Thêm coin cho user.
        Returns: (updated_user_coin, transaction)
        """
        if amount <= 0:
            raise ValueError("Số coin phải lớn hơn 0")

        user_coin = await self.get_or_create_account(user_id)
        
        # Update balance
        user_coin.balance += amount
        if tx_type == CoinTransactionType.PURCHASE:
            user_coin.total_purchased += amount
        
        # Create transaction
        tx = CoinTransactions(
            id=uuid.uuid4(),
            user_id=user_id,
            type=tx_type,
            amount=amount,
            balance_after=user_coin.balance,
            description=description,
            metadata=metadata or {}
        )
        
        self.db.add(tx)
        await self.db.commit()
        await self.db.refresh(user_coin)
        await self.db.refresh(tx)

        return user_coin, tx

    async def deduct_coin(
        self,
        user_id: UUID,
        amount: int,
        tx_type: CoinTransactionType,
        description: str,
        metadata: Optional[dict] = None
    ) -> Tuple[UserCoins, CoinTransactions]:
        """
        Trừ coin của user.
        Returns: (updated_user_coin, transaction)
        Raises: ValueError nếu số dư không đủ
        """
        if amount <= 0:
            raise ValueError("Số coin phải lớn hơn 0")

        user_coin = await self.get_or_create_account(user_id)
        
        if user_coin.balance < amount:
            raise ValueError(f"Số dư không đủ. Cần {amount} coin, có {user_coin.balance} coin")

        # Update balance
        user_coin.balance -= amount
        user_coin.total_spent += amount

        # Create transaction
        tx = CoinTransactions(
            id=uuid.uuid4(),
            user_id=user_id,
            type=tx_type,
            amount=-amount,  # Negative amount for deduction
            balance_after=user_coin.balance,
            description=description,
            metadata=metadata or {}
        )
        
        self.db.add(tx)
        await self.db.commit()
        await self.db.refresh(user_coin)
        await self.db.refresh(tx)

        return user_coin, tx

    # ─── Purchase Coin ─────────────────────────────────────────────────────────

    async def create_purchase_order(
        self,
        user_id: UUID,
        request: PurchaseCoinRequest
    ) -> PurchaseCoinResponse:
        """
        Tạo order mua coin.
        Trong thực tế, đây sẽ gọi payment gateway (VNPAY/MOMO/Zalo).
        Hiện tại mock để test.
        """
        # Xác định số coin và giá
        if request.package_id:
            # Mua theo gói
            coin_amount, bonus_coin, price_vnd = self._get_package_info(request.package_id)
        else:
            # Mua tự chọn
            coin_amount = request.coin_amount
            bonus_coin = self._calculate_bonus(coin_amount)
            price_vnd = coin_amount * COIN_CONVERSION_RATE

        total_coin = coin_amount + bonus_coin
        order_id = f"COIN-{uuid.uuid4().hex[:12].upper()}"

        # Tạo pending transaction (sẽ confirmed khi payment thành công)
        # Trong thực tế, lưu order vào database
        
        return PurchaseCoinResponse(
            order_id=order_id,
            payment_url=f"https://payment.example.com/pay?order={order_id}",  # Mock URL
            coin_amount=coin_amount,
            bonus_coin=bonus_coin,
            total_coin=total_coin,
            price_vnd=price_vnd,
            expires_at=datetime.utcnow()  # 24 hours expiry
        )

    async def confirm_coin_purchase(
        self,
        user_id: UUID,
        order_id: str,
        amount: int,
        bonus_coin: int = 0
    ) -> CoinBalanceResponse:
        """
        Xác nhận thanh toán và cộng coin cho user.
        Called sau khi payment gateway callback thành công.
        """
        total_coin = amount + bonus_coin
        
        user_coin, tx = await self.add_coin(
            user_id=user_id,
            amount=total_coin,
            tx_type=CoinTransactionType.PURCHASE,
            description=f"Mua {amount} coin" + (f" + {bonus_coin} bonus" if bonus_coin else ""),
            metadata={
                "order_id": order_id,
                "base_amount": amount,
                "bonus_amount": bonus_coin,
                "total_amount": total_coin
            }
        )

        return CoinBalanceResponse(
            balance=user_coin.balance,
            total_purchased=user_coin.total_purchased,
            total_spent=user_coin.total_spent,
            conversion_rate=COIN_CONVERSION_RATE
        )

    def _get_package_info(self, package_id: UUID) -> Tuple[int, int, int]:
        """Lấy thông tin gói coin."""
        # Mock data - sau này đọc từ database
        packages = {
            UUID("00000000-0000-0000-0000-000000000001"): (100, 0, 100000),    # 100 coin = 100k
            UUID("00000000-0000-0000-0000-000000000002"): (500, 50, 450000),    # 550 coin = 450k
            UUID("00000000-0000-0000-0000-000000000003"): (1000, 200, 800000), # 1200 coin = 800k
        }
        
        if package_id not in packages:
            raise ValueError("Gói coin không tồn tại")
        
        return packages[package_id]

    def _calculate_bonus(self, coin_amount: int) -> int:
        """Tính bonus coin theo số lượng mua."""
        if coin_amount >= 1000:
            return int(coin_amount * 0.2)  # 20% bonus cho mua >= 1000
        elif coin_amount >= 500:
            return int(coin_amount * 0.1)  # 10% bonus cho mua >= 500
        elif coin_amount >= 100:
            return int(coin_amount * 0.05)  # 5% bonus cho mua >= 100
        return 0

    # ─── Purchase Course with Coin ────────────────────────────────────────────

    async def purchase_course_with_coin(
        self,
        user_id: UUID,
        course_id: UUID
    ) -> PurchaseCourseWithCoinResponse:
        """
        Mua khóa học bằng coin.
        """
        # Lấy thông tin khóa học
        result = await self.db.execute(
            select(Courses).where(Courses.id == course_id)
        )
        course = result.scalar_one_or_none()
        
        if not course:
            return PurchaseCourseWithCoinResponse(
                success=False,
                course_id=course_id,
                coin_spent=0,
                balance_remaining=0,
                message="Khóa học không tồn tại"
            )

        if course.base_price == 0:
            return PurchaseCourseWithCoinResponse(
                success=False,
                course_id=course_id,
                coin_spent=0,
                balance_remaining=0,
                message="Khóa học miễn phí, không cần mua bằng coin"
            )

        # Tính giá coin
        price_coin = course.base_price // COIN_CONVERSION_RATE
        if course.base_price % COIN_CONVERSION_RATE > 0:
            price_coin += 1  # Làm tròn lên

        # Kiểm tra số dư
        user_coin = await self.get_or_create_account(user_id)
        
        if user_coin.balance < price_coin:
            return PurchaseCourseWithCoinResponse(
                success=False,
                course_id=course_id,
                coin_spent=0,
                balance_remaining=user_coin.balance,
                message=f"Số dư không đủ. Cần {price_coin} coin, có {user_coin.balance} coin"
            )

        # Trừ coin
        updated_coin, tx = await self.deduct_coin(
            user_id=user_id,
            amount=price_coin,
            tx_type=CoinTransactionType.COURSE_PURCHASE,
            description=f"Mua khóa học: {course.default_slug or course_id}",
            metadata={
                "course_id": str(course_id),
                "course_name": course.default_slug,
                "price_vnd": course.base_price,
                "price_coin": price_coin
            }
        )

        # TODO: Tạo enrollment cho user (nếu chưa có)
        # enrollment_id = await self._create_enrollment(user_id, course_id)

        return PurchaseCourseWithCoinResponse(
            success=True,
            course_id=course_id,
            coin_spent=price_coin,
            balance_remaining=updated_coin.balance,
            enrollment_id=None,  # TODO: Update khi có enrollment
            message=f"Mua khóa học thành công! Đã trừ {price_coin} coin"
        )

    # ─── Refund ────────────────────────────────────────────────────────────────

    async def refund_course_coin(
        self,
        user_id: UUID,
        request: RefundCourseRequest
    ) -> RefundCourseResponse:
        """
        Hoàn coin khi hủy khóa học.
        """
        # Lấy thông tin khóa học
        result = await self.db.execute(
            select(Courses).where(Courses.id == request.course_id)
        )
        course = result.scalar_one_or_none()
        
        if not course:
            return RefundCourseResponse(
                success=False,
                coin_refunded=0,
                new_balance=0,
                message="Khóa học không tồn tại"
            )

        # Tính giá coin đã thanh toán
        price_coin = course.base_price // COIN_CONVERSION_RATE
        if course.base_price % COIN_CONVERSION_RATE > 0:
            price_coin += 1

        # Hoàn coin (có thể trừ phí hoàn tiền ở đây)
        refund_amount = price_coin  # Hoàn 100% - có thể điều chỉnh
        
        user_coin, tx = await self.add_coin(
            user_id=user_id,
            amount=refund_amount,
            tx_type=CoinTransactionType.REFUND,
            description=f"Hoàn coin khóa học: {course.default_slug or request.course_id}. Lý do: {request.reason or 'Hủy đăng ký'}",
            metadata={
                "course_id": str(request.course_id),
                "original_price_coin": price_coin,
                "refund_reason": request.reason
            }
        )

        return RefundCourseResponse(
            success=True,
            coin_refunded=refund_amount,
            new_balance=user_coin.balance,
            message=f"Đã hoàn {refund_amount} coin vào tài khoản"
        )

    # ─── Admin Operations ──────────────────────────────────────────────────────

    async def admin_add_coin(
        self,
        request: AdminAddCoinRequest,
        admin_id: UUID
    ) -> AdminCoinOperationResponse:
        """Admin thêm coin cho user."""
        try:
            user_coin, tx = await self.add_coin(
                user_id=request.user_id,
                amount=request.amount,
                tx_type=CoinTransactionType.BONUS,
                description=f"Admin thêm coin: {request.reason}",
                metadata={
                    "admin_id": str(admin_id),
                    "reason": request.reason
                }
            )

            return AdminCoinOperationResponse(
                success=True,
                user_id=request.user_id,
                amount=request.amount,
                new_balance=user_coin.balance,
                message=f"Đã thêm {request.amount} coin cho user"
            )
        except Exception as e:
            return AdminCoinOperationResponse(
                success=False,
                user_id=request.user_id,
                amount=0,
                new_balance=0,
                message=f"Lỗi: {str(e)}"
            )

    async def admin_deduct_coin(
        self,
        user_id: UUID,
        amount: int,
        reason: str,
        admin_id: UUID
    ) -> AdminCoinOperationResponse:
        """Admin trừ coin của user."""
        try:
            user_coin, tx = await self.deduct_coin(
                user_id=user_id,
                amount=amount,
                tx_type=CoinTransactionType.BONUS,  # Reuse BONUS type for admin deduction
                description=f"Admin trừ coin: {reason}",
                metadata={
                    "admin_id": str(admin_id),
                    "reason": reason,
                    "action": "deduct"
                }
            )

            return AdminCoinOperationResponse(
                success=True,
                user_id=user_id,
                amount=-amount,
                new_balance=user_coin.balance,
                message=f"Đã trừ {amount} coin của user"
            )
        except ValueError as e:
            return AdminCoinOperationResponse(
                success=False,
                user_id=user_id,
                amount=0,
                new_balance=0,
                message=str(e)
            )

    # ─── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def vnd_to_coin(vnd_amount: int) -> int:
        """Chuyển đổi VND sang coin."""
        coin = vnd_amount // COIN_CONVERSION_RATE
        if vnd_amount % COIN_CONVERSION_RATE > 0:
            coin += 1
        return coin

    @staticmethod
    def coin_to_vnd(coin_amount: int) -> int:
        """Chuyển đổi coin sang VND."""
        return coin_amount * COIN_CONVERSION_RATE
