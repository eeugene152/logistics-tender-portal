# app/seeds/registry.py
from app.crud.user import user_crud
from app.crud.company import company_crud
from app.schemas.auth import SchemaUserRegister
from app.schemas.company import SchemaCompanyCreate
from app.models.users import User
from app.models.company import Company

# Реестр для возможности заливки данных со свежим стартом системы:
# 'название_папки' -> (модель_db, объект_crud, схема_pydantic)
SEED_REGISTRY = {
    'users': {
        'model': User,
        'crud': user_crud,
        'schema': SchemaUserRegister,
        'unique_field': 'email'  # грязный дубль ищем по email
    },
    'companies': {
        'model': Company,
        'crud': company_crud,
        'schema': SchemaCompanyCreate,
        'unique_field': 'company_inn'  # дубль ищем по полю ИНН
    }
}
