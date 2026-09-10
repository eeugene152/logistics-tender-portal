from app.models import Company
from app.crud.crud_base import CRUDBase
from app.schemas.company import SchemaCompanyCreate


# Наследуемся от базового CRUD и передаем 3 типа:
# 1. Модель SQLAlchemy
# 2. Схему создания (Pydantic)
# 3. Для схемы обновления пока передадим SchemaCompanyCreate,
# потом если будет нужно - сделаем и передадим туда SchemaCompanyUpdate.
class CRUDCompany(CRUDBase[Company, SchemaCompanyCreate, SchemaCompanyCreate]):
    pass


# Создаем готовый экземпляр класса, который импортировуем
# в роутеры и сидер
company_crud = CRUDCompany(Company)
