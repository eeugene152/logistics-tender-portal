import enum


class CompanyType(str, enum.Enum):
    CUSTOMER = 'customer'
    CARRIER = 'carrier'
    SUPPLIER = 'supplier'


class UserType(str, enum.Enum):
    ADMIN = 'admin'
    CUSTOMER_MANAGER = 'customer_manager'
    CARRIER_MANAGER = 'carrier_manager'
    SUPPLIER_MANAGER = 'supplier_manager'


class TradeStatus(str, enum.Enum):
    DRAFT = 'draft'
    BIDDING = 'bidding'
    SHIPPING = 'shipping'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
