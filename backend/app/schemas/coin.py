from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class CoinTransactionTypeEnum(str, Enum):
    PURCHASE = 'PURCHASE'
    COURSE_PURCHASE = 'COURSE_PURCHASE'
    REFUND = 'REFUND'
    BONUS = 'BONUS'
    EARN = 'EARN'


# ─── Coin Balance ──────────────────────────────────────────────────────────────

class CoinBalanceRead(BaseModel):
    """Số dư coin của user."""
    user_id: UUID
    balance: int = Field(description="Số coin hiện có")
    total_purchased: int = Field(description="Tổng coin đã mua")
    total_spent: int = Field(description="Tổng coin đã tiêu")

    model_config = {"from_attributes": True}


class CoinBalanceResponse(BaseModel):
    """Response số dư coin với thông tin thêm."""
    balance: int
    total_purchased: int
    total_spent: int
    # Tỷ lệ quy đổi: 1 coin = 1000 VND
    conversion_rate: int = 1000

    model_config = {"from_attributes": True}


# ─── Coin Package (gói coin có thể mua) ──────────────────────────────────────

class CoinPackageBase(BaseModel):
    """Base cho gói coin."""
    name: str = Field(description="Tên gói: 'Starter', 'Pro', 'Enterprise'")
    coin_amount: int = Field(description="Số coin trong gói")
    price_vnd: int = Field(description="Giá VND")
    bonus_coin: int = Field(default=0, description="Số coin bonus thêm")
    is_active: bool = True


class CoinPackageRead(CoinPackageBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class CoinPackageCreate(CoinPackageBase):
    pass


class CoinPackageUpdate(BaseModel):
    name: Optional[str] = None
    coin_amount: Optional[int] = None
    price_vnd: Optional[int] = None
    bonus_coin: Optional[int] = None
    is_active: Optional[bool] = None


# ─── Purchase Coin ─────────────────────────────────────────────────────────────

class PurchaseCoinRequest(BaseModel):
    """Yêu cầu mua coin."""
    package_id: Optional[UUID] = Field(default=None, description="ID gói coin (nếu chọn gói có sẵn)")
    coin_amount: Optional[int] = Field(default=None, description="Số coin tự chọn (nếu không chọn gói)")
    payment_method: str = Field(default="VNPAY", description="Phương thức thanh toán: VNPAY, MOMO, ZALO")

    def model_post_init(self, __context):
        if not self.package_id and not self.coin_amount:
            raise ValueError("Phải chọn package_id hoặc cung cấp coin_amount")


class PurchaseCoinResponse(BaseModel):
    """Response sau khi tạo yêu cầu mua coin."""
    order_id: str
    payment_url: str = Field(description="URL thanh toán VNPAY/MOMO/Zalo")
    coin_amount: int
    bonus_coin: int
    total_coin: int
    price_vnd: int
    expires_at: datetime


# ─── Coin Transaction ──────────────────────────────────────────────────────────

class CoinTransactionRead(BaseModel):
    """Một giao dịch coin."""
    id: UUID
    type: CoinTransactionTypeEnum
    amount: int = Field(description="Số coin thay đổi (+/-)")
    balance_after: int = Field(description="Số dư sau giao dịch")
    description: Optional[str] = None
    metadata: Optional[dict] = {}
    created_at: datetime

    model_config = {"from_attributes": True}


class CoinTransactionListResponse(BaseModel):
    """Danh sách giao dịch coin."""
    transactions: List[CoinTransactionRead]
    total: int
    page: int = 1
    page_size: int = 20


# ─── Course Purchase with Coin ─────────────────────────────────────────────────

class CourseCoinPrice(BaseModel):
    """Giá coin của khóa học."""
    course_id: UUID
    price_vnd: int
    price_coin: int = Field(description="Giá coin = price_vnd / 1000")
    has_discount: bool = False
    discount_percent: int = 0
    final_price_coin: int = Field(description="Giá sau giảm (nếu có)")


class PurchaseCourseWithCoinRequest(BaseModel):
    """Yêu cầu mua khóa học bằng coin."""
    course_id: UUID


class PurchaseCourseWithCoinResponse(BaseModel):
    """Response sau khi mua khóa học bằng coin."""
    success: bool
    course_id: UUID
    coin_spent: int
    balance_remaining: int
    enrollment_id: Optional[UUID] = None
    message: str


class RefundCourseRequest(BaseModel):
    """Yêu cầu hoàn coin khi hủy khóa học."""
    course_id: UUID
    reason: Optional[str] = None


class RefundCourseResponse(BaseModel):
    """Response sau khi hoàn coin."""
    success: bool
    coin_refunded: int
    new_balance: int
    message: str


# ─── Admin ─────────────────────────────────────────────────────────────────────

class AdminCoinStats(BaseModel):
    """Thống kê coin toàn hệ thống (admin)."""
    total_coin_purchased: int
    total_coin_spent: int
    total_active_users: int
    total_transactions: int
    total_revenue_vnd: int


class AdminAddCoinRequest(BaseModel):
    """Admin thêm coin cho user."""
    user_id: UUID
    amount: int = Field(gt=0, description="Số coin cần thêm")
    reason: str = Field(description="Lý do thêm coin: bonus, refund, correction...")


class AdminDeductCoinRequest(BaseModel):
    """Admin trừ coin của user."""
    user_id: UUID
    amount: int = Field(gt=0, description="Số coin cần trừ")
    reason: str = Field(description="Lý do trừ coin")


class AdminCoinOperationResponse(BaseModel):
    """Response sau khi admin thực hiện thao tác coin."""
    success: bool
    user_id: UUID
    amount: int
    new_balance: int
    message: str
