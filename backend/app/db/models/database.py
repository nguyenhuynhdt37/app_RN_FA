from __future__ import annotations
from typing import Any, Optional
import datetime
import decimal
import enum
import uuid

from sqlalchemy import ARRAY, Boolean, CheckConstraint, Date, DateTime, Double, Enum, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, REAL, SmallInteger, String, Text, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import INET, JSONB

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class BillingCycle(str, enum.Enum):
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'


class CorpMemberRole(str, enum.Enum):
    ADMIN = 'admin'
    MEMBER = 'member'


class DisputeStatus(str, enum.Enum):
    OPEN = 'open'
    IN_REVIEW = 'in_review'
    RESOLVED = 'resolved'
    ESCALATED = 'escalated'
    CLOSED = 'closed'


class DriverApprovalStatus(str, enum.Enum):
    PENDING_REVIEW = 'pending_review'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    SUSPENDED = 'suspended'
    BANNED = 'banned'


class DriverDocType(str, enum.Enum):
    ID_CARD_FRONT = 'id_card_front'
    ID_CARD_BACK = 'id_card_back'
    LICENSE_FRONT = 'license_front'
    SELFIE = 'selfie'
    VEHICLE_REGISTRATION = 'vehicle_registration'
    VEHICLE_INSURANCE = 'vehicle_insurance'
    VEHICLE_PHOTO = 'vehicle_photo'


class DriverOnlineStatus(str, enum.Enum):
    OFFLINE = 'offline'
    ONLINE = 'online'
    BUSY = 'busy'
    ON_BREAK = 'on_break'


class FleetApprovalStatus(str, enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    SUSPENDED = 'suspended'


class GenderType(str, enum.Enum):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'


class KycLevel(str, enum.Enum):
    NONE = 'none'
    BASIC = 'basic'
    FULL = 'full'
    ENTERPRISE = 'enterprise'


class MerchantApprovalStatus(str, enum.Enum):
    PENDING_REVIEW = 'pending_review'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    SUSPENDED = 'suspended'


class MerchantStaffRole(str, enum.Enum):
    OWNER = 'owner'
    MANAGER = 'manager'
    STAFF = 'staff'


class MerchantType(str, enum.Enum):
    RESTAURANT = 'restaurant'
    GROCERY = 'grocery'
    PHARMACY = 'pharmacy'
    RETAIL = 'retail'


class NotificationType(str, enum.Enum):
    TRIP_UPDATE = 'trip_update'
    ORDER_UPDATE = 'order_update'
    PAYMENT = 'payment'
    PROMOTION = 'promotion'
    SYSTEM = 'system'
    KYC_STATUS = 'kyc_status'


class OrderStatus(str, enum.Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    PREPARING = 'preparing'
    READY_FOR_PICKUP = 'ready_for_pickup'
    PICKED_UP = 'picked_up'
    DELIVERING = 'delivering'
    DELIVERED = 'delivered'
    CANCELLED_BY_CUSTOMER = 'cancelled_by_customer'
    CANCELLED_BY_MERCHANT = 'cancelled_by_merchant'
    CANCELLED_BY_SYSTEM = 'cancelled_by_system'


class PaymentMethod(str, enum.Enum):
    CASH = 'cash'
    WALLET = 'wallet'
    CARD = 'card'
    CORPORATE = 'corporate'


class PlatformType(str, enum.Enum):
    IOS = 'ios'
    ANDROID = 'android'
    WEB = 'web'


class ServiceType(str, enum.Enum):
    RIDE = 'ride'
    FOOD_DELIVERY = 'food_delivery'
    PARCEL = 'parcel'
    MART = 'mart'


class TransactionType(str, enum.Enum):
    TRIP_CHARGE = 'trip_charge'
    ORDER_CHARGE = 'order_charge'
    TOP_UP = 'top_up'
    WITHDRAWAL = 'withdrawal'
    REFUND = 'refund'
    COMMISSION = 'commission'
    INCENTIVE = 'incentive'
    ADJUSTMENT = 'adjustment'


class TripStatus(str, enum.Enum):
    SEARCHING = 'searching'
    DRIVER_FOUND = 'driver_found'
    DRIVER_ARRIVED = 'driver_arrived'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED_BY_CUSTOMER = 'cancelled_by_customer'
    CANCELLED_BY_DRIVER = 'cancelled_by_driver'
    CANCELLED_BY_SYSTEM = 'cancelled_by_system'


class UserRole(str, enum.Enum):
    CUSTOMER = 'customer'
    DRIVER = 'driver'
    MERCHANT_OWNER = 'merchant_owner'
    MERCHANT_STAFF = 'merchant_staff'
    FLEET_OWNER = 'fleet_owner'
    CORPORATE_ADMIN = 'corporate_admin'
    CORPORATE_USER = 'corporate_user'
    CS_AGENT = 'cs_agent'
    FINANCE = 'finance'
    OPERATOR = 'operator'
    SUPER_ADMIN = 'super_admin'


class VehicleType(str, enum.Enum):
    MOTORBIKE = 'motorbike'
    CAR = 'car'
    VAN = 'van'
    TRUCK = 'truck'
    BICYCLE = 'bicycle'


class WalletOwnerType(str, enum.Enum):
    CUSTOMER = 'customer'
    DRIVER = 'driver'
    MERCHANT = 'merchant'
    FLEET = 'fleet'


class OtpCodes(Base):
    __tablename__ = 'otp_codes'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='otp_codes_pkey'),
        Index('idx_otp_phone_purpose', 'phone', 'purpose'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    purpose: Mapped[str] = mapped_column(String(30), nullable=False)
    attempts: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text('0'))
    is_used: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))


class Promotions(Base):
    __tablename__ = 'promotions'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='promotions_pkey'),
    UniqueConstraint('code', name='promotions_code_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    discount_type: Mapped[str] = mapped_column(String(20), nullable=False)
    discount_value: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    used_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    start_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    end_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    code: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    min_order_value: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    max_discount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    usage_limit: Mapped[Optional[int]] = mapped_column(Integer)

    promotion_usages: Mapped[list['PromotionUsages']] = relationship('PromotionUsages', back_populates='promotion')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pkey'),
    UniqueConstraint('email', name='users_email_key'),
    UniqueConstraint('phone', name='users_phone_key'),
        Index('idx_users_is_active', 'is_active'),
        Index('idx_users_phone', 'phone'),
        Index('idx_users_role', 'role'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, values_callable=lambda cls: [member.value for member in cls], name='user_role'), nullable=False, server_default=text("'customer'::user_role"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    is_phone_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    is_email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    kyc_level: Mapped[KycLevel] = mapped_column(Enum(KycLevel, values_callable=lambda cls: [member.value for member in cls], name='kyc_level'), nullable=False, server_default=text("'none'::kyc_level"))
    preferred_lang: Mapped[str] = mapped_column(String(5), nullable=False, server_default=text("'vi'::character varying"))
    preferred_currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default=text("'VND'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    hashed_password: Mapped[Optional[str]] = mapped_column(Text)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    date_of_birth: Mapped[Optional[datetime.date]] = mapped_column(Date)
    gender: Mapped[Optional[GenderType]] = mapped_column(Enum(GenderType, values_callable=lambda cls: [member.value for member in cls], name='gender_type'))
    device_token: Mapped[Optional[str]] = mapped_column(Text)
    device_platform: Mapped[Optional[PlatformType]] = mapped_column(Enum(PlatformType, values_callable=lambda cls: [member.value for member in cls], name='platform_type'))
    last_seen_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    audit_logs: Mapped[list['AuditLogs']] = relationship('AuditLogs', back_populates='actor')
    corporate_accounts: Mapped[list['CorporateAccounts']] = relationship('CorporateAccounts', back_populates='admin_user')
    customer_profiles: Mapped['CustomerProfiles'] = relationship('CustomerProfiles', uselist=False, back_populates='user')
    disputes_assigned_to: Mapped[list['Disputes']] = relationship('Disputes', foreign_keys='[Disputes.assigned_to]', back_populates='users')
    disputes_reported: Mapped[list['Disputes']] = relationship('Disputes', foreign_keys='[Disputes.reported_id]', back_populates='reported')
    disputes_reporter: Mapped[list['Disputes']] = relationship('Disputes', foreign_keys='[Disputes.reporter_id]', back_populates='reporter')
    fleets: Mapped['Fleets'] = relationship('Fleets', uselist=False, back_populates='owner_user')
    merchant_businesses: Mapped[list['MerchantBusinesses']] = relationship('MerchantBusinesses', back_populates='owner_user')
    notifications: Mapped[list['Notifications']] = relationship('Notifications', back_populates='user')
    oauth_accounts: Mapped[list['OauthAccounts']] = relationship('OauthAccounts', back_populates='user')
    pricing_rules: Mapped[list['PricingRules']] = relationship('PricingRules', back_populates='users')
    promotion_usages: Mapped[list['PromotionUsages']] = relationship('PromotionUsages', back_populates='user')
    saved_places: Mapped[list['SavedPlaces']] = relationship('SavedPlaces', back_populates='user')
    corporate_members: Mapped[list['CorporateMembers']] = relationship('CorporateMembers', back_populates='user')
    dispute_messages: Mapped[list['DisputeMessages']] = relationship('DisputeMessages', back_populates='sender')
    driver_profiles_approved_by: Mapped[list['DriverProfiles']] = relationship('DriverProfiles', foreign_keys='[DriverProfiles.approved_by]', back_populates='users')
    driver_profiles_user: Mapped['DriverProfiles'] = relationship('DriverProfiles', uselist=False, foreign_keys='[DriverProfiles.user_id]', back_populates='users_user')
    trips_customer: Mapped[list['Trips']] = relationship('Trips', foreign_keys='[Trips.customer_id]', back_populates='customer')
    trips_driver: Mapped[list['Trips']] = relationship('Trips', foreign_keys='[Trips.driver_id]', back_populates='driver')
    driver_documents: Mapped[list['DriverDocuments']] = relationship('DriverDocuments', back_populates='users')
    merchant_staff: Mapped[list['MerchantStaff']] = relationship('MerchantStaff', back_populates='user')
    orders_customer: Mapped[list['Orders']] = relationship('Orders', foreign_keys='[Orders.customer_id]', back_populates='customer')
    orders_driver: Mapped[list['Orders']] = relationship('Orders', foreign_keys='[Orders.driver_id]', back_populates='driver')


class Wallets(Base):
    __tablename__ = 'wallets'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='wallets_pkey'),
    UniqueConstraint('owner_id', 'owner_type', name='wallets_owner_id_owner_type_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    owner_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    owner_type: Mapped[WalletOwnerType] = mapped_column(Enum(WalletOwnerType, values_callable=lambda cls: [member.value for member in cls], name='wallet_owner_type'), nullable=False)
    balance: Mapped[decimal.Decimal] = mapped_column(Numeric(12, 2), nullable=False, server_default=text('0'))
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default=text("'VND'::character varying"))
    is_frozen: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    wallet_transactions: Mapped[list['WalletTransactions']] = relationship('WalletTransactions', back_populates='wallet')


class AuditLogs(Base):
    __tablename__ = 'audit_logs'
    __table_args__ = (
    ForeignKeyConstraint(['actor_id'], ['public.users.id'], name='audit_logs_actor_id_fkey'),
        PrimaryKeyConstraint('id', name='audit_logs_pkey'),
        Index('idx_audit_actor', 'actor_id', 'created_at'),
        Index('idx_audit_target', 'target_type', 'target_id'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    actor_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    target_type: Mapped[Optional[str]] = mapped_column(String(50))
    target_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    old_value: Mapped[Optional[dict]] = mapped_column(JSONB)
    new_value: Mapped[Optional[dict]] = mapped_column(JSONB)
    ip_address: Mapped[Optional[Any]] = mapped_column(INET)
    user_agent: Mapped[Optional[str]] = mapped_column(Text)

    actor: Mapped['Users'] = relationship('Users', back_populates='audit_logs')


class CorporateAccounts(Base):
    __tablename__ = 'corporate_accounts'
    __table_args__ = (
    ForeignKeyConstraint(['admin_user_id'], ['public.users.id'], ondelete='CASCADE', name='corporate_accounts_admin_user_id_fkey'),
        PrimaryKeyConstraint('id', name='corporate_accounts_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    admin_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    billing_email: Mapped[str] = mapped_column(String(255), nullable=False)
    current_spent: Mapped[decimal.Decimal] = mapped_column(Numeric(12, 2), nullable=False, server_default=text('0'))
    billing_cycle: Mapped[BillingCycle] = mapped_column(Enum(BillingCycle, values_callable=lambda cls: [member.value for member in cls], name='billing_cycle'), nullable=False, server_default=text("'monthly'::billing_cycle"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    tax_code: Mapped[Optional[str]] = mapped_column(String(20))
    monthly_budget: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))

    admin_user: Mapped['Users'] = relationship('Users', back_populates='corporate_accounts')
    corporate_members: Mapped[list['CorporateMembers']] = relationship('CorporateMembers', back_populates='corporate')
    trips: Mapped[list['Trips']] = relationship('Trips', back_populates='corporate')
    orders: Mapped[list['Orders']] = relationship('Orders', back_populates='corporate')


class CustomerProfiles(Base):
    __tablename__ = 'customer_profiles'
    __table_args__ = (
    ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='customer_profiles_user_id_fkey'),
        PrimaryKeyConstraint('id', name='customer_profiles_pkey'),
    UniqueConstraint('user_id', name='customer_profiles_user_id_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    default_payment: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod, values_callable=lambda cls: [member.value for member in cls], name='payment_method'), nullable=False, server_default=text("'cash'::payment_method"))
    rating: Mapped[decimal.Decimal] = mapped_column(Numeric(3, 2), nullable=False, server_default=text('5.00'))
    rating_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    total_trips: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    loyalty_points: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    is_pet_friendly: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    home_address: Mapped[Optional[str]] = mapped_column(Text)
    home_lat: Mapped[Optional[float]] = mapped_column(Double(53))
    home_lng: Mapped[Optional[float]] = mapped_column(Double(53))
    work_address: Mapped[Optional[str]] = mapped_column(Text)
    work_lat: Mapped[Optional[float]] = mapped_column(Double(53))
    work_lng: Mapped[Optional[float]] = mapped_column(Double(53))
    preferred_vehicle_type: Mapped[Optional[VehicleType]] = mapped_column(Enum(VehicleType, values_callable=lambda cls: [member.value for member in cls], name='vehicle_type'))

    user: Mapped['Users'] = relationship('Users', back_populates='customer_profiles')


class Disputes(Base):
    __tablename__ = 'disputes'
    __table_args__ = (
    ForeignKeyConstraint(['assigned_to'], ['public.users.id'], name='disputes_assigned_to_fkey'),
    ForeignKeyConstraint(['reported_id'], ['public.users.id'], name='disputes_reported_id_fkey'),
    ForeignKeyConstraint(['reporter_id'], ['public.users.id'], name='disputes_reporter_id_fkey'),
        PrimaryKeyConstraint('id', name='disputes_pkey'),
        Index('idx_disputes_assigned', 'assigned_to'),
        Index('idx_disputes_status', 'status'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    reporter_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[DisputeStatus] = mapped_column(Enum(DisputeStatus, values_callable=lambda cls: [member.value for member in cls], name='dispute_status'), nullable=False, server_default=text("'open'::dispute_status"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    reported_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    ref_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    ref_type: Mapped[Optional[str]] = mapped_column(String(20))
    assigned_to: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    resolution: Mapped[Optional[str]] = mapped_column(Text)
    resolved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[assigned_to], back_populates='disputes_assigned_to')
    reported: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[reported_id], back_populates='disputes_reported')
    reporter: Mapped['Users'] = relationship('Users', foreign_keys=[reporter_id], back_populates='disputes_reporter')
    dispute_messages: Mapped[list['DisputeMessages']] = relationship('DisputeMessages', back_populates='dispute')


class Fleets(Base):
    __tablename__ = 'fleets'
    __table_args__ = (
    ForeignKeyConstraint(['owner_user_id'], ['public.users.id'], ondelete='CASCADE', name='fleets_owner_user_id_fkey'),
        PrimaryKeyConstraint('id', name='fleets_pkey'),
    UniqueConstraint('owner_user_id', name='fleets_owner_user_id_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    owner_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    fleet_name: Mapped[str] = mapped_column(String(150), nullable=False)
    approval_status: Mapped[FleetApprovalStatus] = mapped_column(Enum(FleetApprovalStatus, values_callable=lambda cls: [member.value for member in cls], name='fleet_approval_status'), nullable=False, server_default=text("'pending'::fleet_approval_status"))
    commission_rate: Mapped[decimal.Decimal] = mapped_column(Numeric(4, 3), nullable=False, server_default=text('0.100'))
    total_drivers: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    business_license: Mapped[Optional[str]] = mapped_column(String(50))

    owner_user: Mapped['Users'] = relationship('Users', back_populates='fleets')
    driver_profiles: Mapped[list['DriverProfiles']] = relationship('DriverProfiles', back_populates='fleet')


class MerchantBusinesses(Base):
    __tablename__ = 'merchant_businesses'
    __table_args__ = (
    ForeignKeyConstraint(['owner_user_id'], ['public.users.id'], ondelete='CASCADE', name='merchant_businesses_owner_user_id_fkey'),
        PrimaryKeyConstraint('id', name='merchant_businesses_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    owner_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    business_name: Mapped[str] = mapped_column(String(200), nullable=False)
    business_type: Mapped[MerchantType] = mapped_column(Enum(MerchantType, values_callable=lambda cls: [member.value for member in cls], name='merchant_type'), nullable=False, server_default=text("'restaurant'::merchant_type"))
    approval_status: Mapped[MerchantApprovalStatus] = mapped_column(Enum(MerchantApprovalStatus, values_callable=lambda cls: [member.value for member in cls], name='merchant_approval_status'), nullable=False, server_default=text("'pending_review'::merchant_approval_status"))
    commission_rate: Mapped[decimal.Decimal] = mapped_column(Numeric(4, 3), nullable=False, server_default=text('0.200'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    tax_code: Mapped[Optional[str]] = mapped_column(String(20))
    business_license_url: Mapped[Optional[str]] = mapped_column(Text)
    bank_account_number: Mapped[Optional[str]] = mapped_column(String(30))
    bank_name: Mapped[Optional[str]] = mapped_column(String(100))
    bank_account_name: Mapped[Optional[str]] = mapped_column(String(150))

    owner_user: Mapped['Users'] = relationship('Users', back_populates='merchant_businesses')
    merchant_outlets: Mapped[list['MerchantOutlets']] = relationship('MerchantOutlets', back_populates='business')


class Notifications(Base):
    __tablename__ = 'notifications'
    __table_args__ = (
    ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='notifications_user_id_fkey'),
        PrimaryKeyConstraint('id', name='notifications_pkey'),
        Index('idx_notifications_user', 'user_id', 'is_read', 'created_at'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType, values_callable=lambda cls: [member.value for member in cls], name='notification_type'), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    data: Mapped[Optional[dict]] = mapped_column(JSONB)
    sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    read_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    user: Mapped['Users'] = relationship('Users', back_populates='notifications')


class OauthAccounts(Base):
    __tablename__ = 'oauth_accounts'
    __table_args__ = (
    ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='oauth_accounts_user_id_fkey'),
        PrimaryKeyConstraint('id', name='oauth_accounts_pkey'),
    UniqueConstraint('provider', 'provider_uid', name='oauth_accounts_provider_provider_uid_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    provider_uid: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    access_token: Mapped[Optional[str]] = mapped_column(Text)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text)
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    user: Mapped['Users'] = relationship('Users', back_populates='oauth_accounts')


class PricingRules(Base):
    __tablename__ = 'pricing_rules'
    __table_args__ = (
    ForeignKeyConstraint(['updated_by'], ['public.users.id'], name='pricing_rules_updated_by_fkey'),
        PrimaryKeyConstraint('id', name='pricing_rules_pkey'),
    UniqueConstraint('service_type', 'vehicle_type', 'city', name='pricing_rules_service_type_vehicle_type_city_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    service_type: Mapped[ServiceType] = mapped_column(Enum(ServiceType, values_callable=lambda cls: [member.value for member in cls], name='service_type'), nullable=False)
    vehicle_type: Mapped[VehicleType] = mapped_column(Enum(VehicleType, values_callable=lambda cls: [member.value for member in cls], name='vehicle_type'), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False, server_default=text("'hanoi'::character varying"))
    base_fare: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    per_km_rate: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    per_minute_rate: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False, server_default=text('0'))
    min_fare: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    surge_threshold: Mapped[decimal.Decimal] = mapped_column(Numeric(4, 2), nullable=False, server_default=text('1.5'))
    max_surge: Mapped[decimal.Decimal] = mapped_column(Numeric(4, 2), nullable=False, server_default=text('3.0'))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    users: Mapped[Optional['Users']] = relationship('Users', back_populates='pricing_rules')


class PromotionUsages(Base):
    __tablename__ = 'promotion_usages'
    __table_args__ = (
    ForeignKeyConstraint(['promotion_id'], ['public.promotions.id'], name='promotion_usages_promotion_id_fkey'),
    ForeignKeyConstraint(['user_id'], ['public.users.id'], name='promotion_usages_user_id_fkey'),
        PrimaryKeyConstraint('id', name='promotion_usages_pkey'),
    UniqueConstraint('promotion_id', 'user_id', 'ref_id', name='promotion_usages_promotion_id_user_id_ref_id_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    promotion_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    ref_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    ref_type: Mapped[str] = mapped_column(String(20), nullable=False)
    discount_applied: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    promotion: Mapped['Promotions'] = relationship('Promotions', back_populates='promotion_usages')
    user: Mapped['Users'] = relationship('Users', back_populates='promotion_usages')


class SavedPlaces(Base):
    __tablename__ = 'saved_places'
    __table_args__ = (
    ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='saved_places_user_id_fkey'),
        PrimaryKeyConstraint('id', name='saved_places_pkey'),
        Index('idx_saved_places_user', 'user_id'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    lat: Mapped[float] = mapped_column(Double(53), nullable=False)
    lng: Mapped[float] = mapped_column(Double(53), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    icon: Mapped[Optional[str]] = mapped_column(String(50))

    user: Mapped['Users'] = relationship('Users', back_populates='saved_places')


class WalletTransactions(Base):
    __tablename__ = 'wallet_transactions'
    __table_args__ = (
    ForeignKeyConstraint(['wallet_id'], ['public.wallets.id'], name='wallet_transactions_wallet_id_fkey'),
        PrimaryKeyConstraint('id', name='wallet_transactions_pkey'),
        Index('idx_wallet_tx_ref', 'ref_id', 'ref_type'),
        Index('idx_wallet_tx_wallet', 'wallet_id', 'created_at'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    wallet_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType, values_callable=lambda cls: [member.value for member in cls], name='transaction_type'), nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    balance_after: Mapped[decimal.Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    ref_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    ref_type: Mapped[Optional[str]] = mapped_column(String(30))
    description: Mapped[Optional[str]] = mapped_column(Text)
    metadata_: Mapped[Optional[dict]] = mapped_column('metadata', JSONB)

    wallet: Mapped['Wallets'] = relationship('Wallets', back_populates='wallet_transactions')


class CorporateMembers(Base):
    __tablename__ = 'corporate_members'
    __table_args__ = (
    ForeignKeyConstraint(['corporate_id'], ['public.corporate_accounts.id'], ondelete='CASCADE', name='corporate_members_corporate_id_fkey'),
    ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='corporate_members_user_id_fkey'),
        PrimaryKeyConstraint('id', name='corporate_members_pkey'),
    UniqueConstraint('corporate_id', 'user_id', name='corporate_members_corporate_id_user_id_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    corporate_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    member_role: Mapped[CorpMemberRole] = mapped_column(Enum(CorpMemberRole, values_callable=lambda cls: [member.value for member in cls], name='corp_member_role'), nullable=False, server_default=text("'member'::corp_member_role"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    trip_budget: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))

    corporate: Mapped['CorporateAccounts'] = relationship('CorporateAccounts', back_populates='corporate_members')
    user: Mapped['Users'] = relationship('Users', back_populates='corporate_members')


class DisputeMessages(Base):
    __tablename__ = 'dispute_messages'
    __table_args__ = (
    ForeignKeyConstraint(['dispute_id'], ['public.disputes.id'], ondelete='CASCADE', name='dispute_messages_dispute_id_fkey'),
    ForeignKeyConstraint(['sender_id'], ['public.users.id'], name='dispute_messages_sender_id_fkey'),
        PrimaryKeyConstraint('id', name='dispute_messages_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    dispute_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    sender_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    attachment_url: Mapped[Optional[str]] = mapped_column(Text)

    dispute: Mapped['Disputes'] = relationship('Disputes', back_populates='dispute_messages')
    sender: Mapped['Users'] = relationship('Users', back_populates='dispute_messages')


class DriverProfiles(Base):
    __tablename__ = 'driver_profiles'
    __table_args__ = (
    ForeignKeyConstraint(['approved_by'], ['public.users.id'], name='driver_profiles_approved_by_fkey'),
    ForeignKeyConstraint(['fleet_id'], ['public.fleets.id'], ondelete='SET NULL', name='fk_driver_fleet'),
    ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='driver_profiles_user_id_fkey'),
        PrimaryKeyConstraint('id', name='driver_profiles_pkey'),
    UniqueConstraint('id_card_number', name='driver_profiles_id_card_number_key'),
    UniqueConstraint('license_number', name='driver_profiles_license_number_key'),
    UniqueConstraint('user_id', name='driver_profiles_user_id_key'),
    UniqueConstraint('vehicle_plate', name='driver_profiles_vehicle_plate_key'),
        Index('idx_driver_approval', 'approval_status'),
        Index('idx_driver_lat', 'current_lat', postgresql_where='(is_online = true)'),
        Index('idx_driver_lng', 'current_lng', postgresql_where='(is_online = true)'),
        Index('idx_driver_online', 'is_online', 'current_status'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    id_card_number: Mapped[str] = mapped_column(String(20), nullable=False)
    license_number: Mapped[str] = mapped_column(String(30), nullable=False)
    approval_status: Mapped[DriverApprovalStatus] = mapped_column(Enum(DriverApprovalStatus, values_callable=lambda cls: [member.value for member in cls], name='driver_approval_status'), nullable=False, server_default=text("'pending_review'::driver_approval_status"))
    service_types: Mapped[list[ServiceType]] = mapped_column(ARRAY(Enum(ServiceType, values_callable=lambda cls: [member.value for member in cls], name='service_type')), nullable=False, server_default=text("'{ride}'::service_type[]"))
    vehicle_type: Mapped[VehicleType] = mapped_column(Enum(VehicleType, values_callable=lambda cls: [member.value for member in cls], name='vehicle_type'), nullable=False, server_default=text("'motorbike'::vehicle_type"))
    vehicle_plate: Mapped[str] = mapped_column(String(20), nullable=False)
    is_online: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    current_status: Mapped[DriverOnlineStatus] = mapped_column(Enum(DriverOnlineStatus, values_callable=lambda cls: [member.value for member in cls], name='driver_online_status'), nullable=False, server_default=text("'offline'::driver_online_status"))
    rating: Mapped[decimal.Decimal] = mapped_column(Numeric(3, 2), nullable=False, server_default=text('5.00'))
    rating_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    total_trips: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    total_distance_km: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False, server_default=text('0'))
    acceptance_rate: Mapped[decimal.Decimal] = mapped_column(Numeric(4, 3), nullable=False, server_default=text('1.000'))
    completion_rate: Mapped[decimal.Decimal] = mapped_column(Numeric(4, 3), nullable=False, server_default=text('1.000'))
    cancellation_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    today_trips: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    today_earnings: Mapped[decimal.Decimal] = mapped_column(Numeric(12, 2), nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    fleet_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    license_class: Mapped[Optional[str]] = mapped_column(String(5))
    license_expiry: Mapped[Optional[datetime.date]] = mapped_column(Date)
    approved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
    suspension_reason: Mapped[Optional[str]] = mapped_column(Text)
    suspension_until: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    vehicle_brand: Mapped[Optional[str]] = mapped_column(String(50))
    vehicle_model: Mapped[Optional[str]] = mapped_column(String(50))
    vehicle_year: Mapped[Optional[int]] = mapped_column(SmallInteger)
    vehicle_color: Mapped[Optional[str]] = mapped_column(String(30))
    vehicle_insurance_expiry: Mapped[Optional[datetime.date]] = mapped_column(Date)
    current_lat: Mapped[Optional[float]] = mapped_column(Double(53))
    current_lng: Mapped[Optional[float]] = mapped_column(Double(53))
    current_heading: Mapped[Optional[float]] = mapped_column(REAL)
    last_location_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    bank_account_number: Mapped[Optional[str]] = mapped_column(String(30))
    bank_name: Mapped[Optional[str]] = mapped_column(String(100))
    bank_account_name: Mapped[Optional[str]] = mapped_column(String(150))
    shift_started_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[approved_by], back_populates='driver_profiles_approved_by')
    fleet: Mapped[Optional['Fleets']] = relationship('Fleets', back_populates='driver_profiles')
    users_user: Mapped['Users'] = relationship('Users', foreign_keys=[user_id], back_populates='driver_profiles_user')
    driver_documents: Mapped[list['DriverDocuments']] = relationship('DriverDocuments', back_populates='driver')


class MerchantOutlets(Base):
    __tablename__ = 'merchant_outlets'
    __table_args__ = (
    ForeignKeyConstraint(['business_id'], ['public.merchant_businesses.id'], ondelete='CASCADE', name='merchant_outlets_business_id_fkey'),
        PrimaryKeyConstraint('id', name='merchant_outlets_pkey'),
        Index('idx_outlet_lat', 'lat'),
        Index('idx_outlet_lng', 'lng'),
        Index('idx_outlet_open', 'is_open', 'is_busy'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    business_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    outlet_name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    lat: Mapped[float] = mapped_column(Double(53), nullable=False)
    lng: Mapped[float] = mapped_column(Double(53), nullable=False)
    is_open: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    is_busy: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    operating_hours: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    rating: Mapped[decimal.Decimal] = mapped_column(Numeric(3, 2), nullable=False, server_default=text('5.00'))
    rating_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    avg_prep_time: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text('20'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    banner_url: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    district: Mapped[Optional[str]] = mapped_column(String(100))
    busy_until: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    business: Mapped['MerchantBusinesses'] = relationship('MerchantBusinesses', back_populates='merchant_outlets')
    menu_categories: Mapped[list['MenuCategories']] = relationship('MenuCategories', back_populates='outlet')
    merchant_staff: Mapped[list['MerchantStaff']] = relationship('MerchantStaff', back_populates='outlet')
    orders: Mapped[list['Orders']] = relationship('Orders', back_populates='outlet')
    menu_items: Mapped[list['MenuItems']] = relationship('MenuItems', back_populates='outlet')


class Trips(Base):
    __tablename__ = 'trips'
    __table_args__ = (
    CheckConstraint('customer_rating >= 1 AND customer_rating <= 5', name='trips_customer_rating_check'),
    CheckConstraint('driver_rating >= 1 AND driver_rating <= 5', name='trips_driver_rating_check'),
    ForeignKeyConstraint(['corporate_id'], ['public.corporate_accounts.id'], name='trips_corporate_id_fkey'),
    ForeignKeyConstraint(['customer_id'], ['public.users.id'], name='trips_customer_id_fkey'),
    ForeignKeyConstraint(['driver_id'], ['public.users.id'], name='trips_driver_id_fkey'),
        PrimaryKeyConstraint('id', name='trips_pkey'),
        Index('idx_trips_customer', 'customer_id', 'created_at'),
        Index('idx_trips_driver', 'driver_id', 'created_at'),
        Index('idx_trips_status', 'status'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    customer_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    status: Mapped[TripStatus] = mapped_column(Enum(TripStatus, values_callable=lambda cls: [member.value for member in cls], name='trip_status'), nullable=False, server_default=text("'searching'::trip_status"))
    vehicle_type: Mapped[VehicleType] = mapped_column(Enum(VehicleType, values_callable=lambda cls: [member.value for member in cls], name='vehicle_type'), nullable=False, server_default=text("'motorbike'::vehicle_type"))
    pickup_address: Mapped[str] = mapped_column(Text, nullable=False)
    pickup_lat: Mapped[float] = mapped_column(Double(53), nullable=False)
    pickup_lng: Mapped[float] = mapped_column(Double(53), nullable=False)
    dest_address: Mapped[str] = mapped_column(Text, nullable=False)
    dest_lat: Mapped[float] = mapped_column(Double(53), nullable=False)
    dest_lng: Mapped[float] = mapped_column(Double(53), nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod, values_callable=lambda cls: [member.value for member in cls], name='payment_method'), nullable=False, server_default=text("'cash'::payment_method"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    driver_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    corporate_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    estimated_distance: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(8, 2))
    estimated_duration: Mapped[Optional[int]] = mapped_column(Integer)
    base_fare: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    surge_multiplier: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(4, 2), server_default=text('1.00'))
    final_fare: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    driver_accepted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    driver_arrived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    cancelled_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    cancel_reason: Mapped[Optional[str]] = mapped_column(Text)
    customer_rating: Mapped[Optional[int]] = mapped_column(SmallInteger)
    driver_rating: Mapped[Optional[int]] = mapped_column(SmallInteger)
    customer_review: Mapped[Optional[str]] = mapped_column(Text)
    driver_review: Mapped[Optional[str]] = mapped_column(Text)

    corporate: Mapped[Optional['CorporateAccounts']] = relationship('CorporateAccounts', back_populates='trips')
    customer: Mapped['Users'] = relationship('Users', foreign_keys=[customer_id], back_populates='trips_customer')
    driver: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[driver_id], back_populates='trips_driver')


class DriverDocuments(Base):
    __tablename__ = 'driver_documents'
    __table_args__ = (
    ForeignKeyConstraint(['driver_id'], ['public.driver_profiles.id'], ondelete='CASCADE', name='driver_documents_driver_id_fkey'),
    ForeignKeyConstraint(['verified_by'], ['public.users.id'], name='driver_documents_verified_by_fkey'),
        PrimaryKeyConstraint('id', name='driver_documents_pkey'),
    UniqueConstraint('driver_id', 'doc_type', name='driver_documents_driver_id_doc_type_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    driver_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    doc_type: Mapped[DriverDocType] = mapped_column(Enum(DriverDocType, values_callable=lambda cls: [member.value for member in cls], name='driver_doc_type'), nullable=False)
    doc_url: Mapped[str] = mapped_column(Text, nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    verified_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    expires_at: Mapped[Optional[datetime.date]] = mapped_column(Date)

    driver: Mapped['DriverProfiles'] = relationship('DriverProfiles', back_populates='driver_documents')
    users: Mapped[Optional['Users']] = relationship('Users', back_populates='driver_documents')


class MenuCategories(Base):
    __tablename__ = 'menu_categories'
    __table_args__ = (
    ForeignKeyConstraint(['outlet_id'], ['public.merchant_outlets.id'], ondelete='CASCADE', name='menu_categories_outlet_id_fkey'),
        PrimaryKeyConstraint('id', name='menu_categories_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    outlet_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text('0'))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    outlet: Mapped['MerchantOutlets'] = relationship('MerchantOutlets', back_populates='menu_categories')
    menu_items: Mapped[list['MenuItems']] = relationship('MenuItems', back_populates='category')


class MerchantStaff(Base):
    __tablename__ = 'merchant_staff'
    __table_args__ = (
    ForeignKeyConstraint(['outlet_id'], ['public.merchant_outlets.id'], ondelete='CASCADE', name='merchant_staff_outlet_id_fkey'),
    ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='merchant_staff_user_id_fkey'),
        PrimaryKeyConstraint('id', name='merchant_staff_pkey'),
    UniqueConstraint('outlet_id', 'user_id', name='merchant_staff_outlet_id_user_id_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    outlet_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    staff_role: Mapped[MerchantStaffRole] = mapped_column(Enum(MerchantStaffRole, values_callable=lambda cls: [member.value for member in cls], name='merchant_staff_role'), nullable=False, server_default=text("'staff'::merchant_staff_role"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    outlet: Mapped['MerchantOutlets'] = relationship('MerchantOutlets', back_populates='merchant_staff')
    user: Mapped['Users'] = relationship('Users', back_populates='merchant_staff')


class Orders(Base):
    __tablename__ = 'orders'
    __table_args__ = (
    CheckConstraint('driver_rating >= 1 AND driver_rating <= 5', name='orders_driver_rating_check'),
    CheckConstraint('merchant_rating >= 1 AND merchant_rating <= 5', name='orders_merchant_rating_check'),
    ForeignKeyConstraint(['corporate_id'], ['public.corporate_accounts.id'], name='orders_corporate_id_fkey'),
    ForeignKeyConstraint(['customer_id'], ['public.users.id'], name='orders_customer_id_fkey'),
    ForeignKeyConstraint(['driver_id'], ['public.users.id'], name='orders_driver_id_fkey'),
    ForeignKeyConstraint(['outlet_id'], ['public.merchant_outlets.id'], name='orders_outlet_id_fkey'),
        PrimaryKeyConstraint('id', name='orders_pkey'),
        Index('idx_orders_customer', 'customer_id', 'created_at'),
        Index('idx_orders_driver', 'driver_id', 'created_at'),
        Index('idx_orders_outlet', 'outlet_id', 'created_at'),
        Index('idx_orders_status', 'status'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    customer_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    outlet_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus, values_callable=lambda cls: [member.value for member in cls], name='order_status'), nullable=False, server_default=text("'pending'::order_status"))
    delivery_address: Mapped[str] = mapped_column(Text, nullable=False)
    delivery_lat: Mapped[float] = mapped_column(Double(53), nullable=False)
    delivery_lng: Mapped[float] = mapped_column(Double(53), nullable=False)
    subtotal: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False, server_default=text('0'))
    delivery_fee: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False, server_default=text('0'))
    discount_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False, server_default=text('0'))
    total_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False, server_default=text('0'))
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod, values_callable=lambda cls: [member.value for member in cls], name='payment_method'), nullable=False, server_default=text("'cash'::payment_method"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    driver_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    corporate_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    delivery_notes: Mapped[Optional[str]] = mapped_column(Text)
    estimated_prep_time: Mapped[Optional[int]] = mapped_column(Integer)
    estimated_delivery_time: Mapped[Optional[int]] = mapped_column(Integer)
    confirmed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    ready_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    picked_up_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    delivered_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    cancelled_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    cancel_reason: Mapped[Optional[str]] = mapped_column(Text)
    merchant_rating: Mapped[Optional[int]] = mapped_column(SmallInteger)
    driver_rating: Mapped[Optional[int]] = mapped_column(SmallInteger)
    merchant_review: Mapped[Optional[str]] = mapped_column(Text)

    corporate: Mapped[Optional['CorporateAccounts']] = relationship('CorporateAccounts', back_populates='orders')
    customer: Mapped['Users'] = relationship('Users', foreign_keys=[customer_id], back_populates='orders_customer')
    driver: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[driver_id], back_populates='orders_driver')
    outlet: Mapped['MerchantOutlets'] = relationship('MerchantOutlets', back_populates='orders')
    order_items: Mapped[list['OrderItems']] = relationship('OrderItems', back_populates='order')


class MenuItems(Base):
    __tablename__ = 'menu_items'
    __table_args__ = (
    ForeignKeyConstraint(['category_id'], ['public.menu_categories.id'], ondelete='CASCADE', name='menu_items_category_id_fkey'),
    ForeignKeyConstraint(['outlet_id'], ['public.merchant_outlets.id'], ondelete='CASCADE', name='menu_items_outlet_id_fkey'),
        PrimaryKeyConstraint('id', name='menu_items_pkey'),
        Index('idx_menu_items_outlet', 'outlet_id', 'is_available'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    category_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    outlet_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_url: Mapped[Optional[str]] = mapped_column(Text)

    category: Mapped['MenuCategories'] = relationship('MenuCategories', back_populates='menu_items')
    outlet: Mapped['MerchantOutlets'] = relationship('MerchantOutlets', back_populates='menu_items')


class OrderItems(Base):
    __tablename__ = 'order_items'
    __table_args__ = (
    ForeignKeyConstraint(['order_id'], ['public.orders.id'], ondelete='CASCADE', name='order_items_order_id_fkey'),
        PrimaryKeyConstraint('id', name='order_items_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    order_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    menu_item_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    unit_price: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text('1'))
    subtotal: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    order: Mapped['Orders'] = relationship('Orders', back_populates='order_items')

# === AUTO FIX SUMMARY ===
# Generated by fix_sqlacodegen_models.py v2
# • Fixed class inheritance → Base
# • Fixed indented ForeignKeyConstraint
# • Injected relationship() with back_populates
# • Fixed UUID / ARRAY / JSONB type hints
# • Added necessary imports
# ==========================
