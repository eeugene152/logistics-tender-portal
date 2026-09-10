from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.session import get_async_session
from app.core.seeder import DataSeeder
from app.schemas.company import SchemaCompanyCreate


router = APIRouter()


@router.post("/import/")
async def import_companies(
    file: UploadFile = File(...), session: AsyncSession = Depends(
        get_async_session
    )
):
    file_bytes = await file.read()
    # Передаем кортеж (байты, имя_файла) в параметр memory_data
    report = await DataSeeder.run_seed(
        session=session,
        crud_instance=company_crud,
        schema_create=SchemaCompanyCreate,
        memory_data=(file_bytes, file.filename)
    )
    return report