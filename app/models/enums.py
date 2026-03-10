import enum


class CompanyType(str, enum.Enum):
    CUSTOMER = 'customer'
    CARRIER = 'carrier'
    SUPPLIER = 'supplier'
