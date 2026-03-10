from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base, str_uniq
from enums import CompanyType


class Company(Base):
