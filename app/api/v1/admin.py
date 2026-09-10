from enum import Enum
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_async_session
from app.core.seeder import UniversalDataSeeder
from app.seeds.registry import SEED_REGISTRY

router = APIRouter(prefix='/admin', tags=['Admin Panel'])


# по принципу DRY Создаем Enum на основе ключей нашего реестра SEED_REGISTRY.
# "на лету". ImportEntity.companies, ImportEntity.users и т.д.
# {k: k for k in SEED_REGISTRY.keys()} превращает
# ключи в словарь вида {"companies": "companies"}
ImportEntity = Enum(
    "ImportEntity",
    {key: key for key in SEED_REGISTRY.keys()},
    type=str
)
# вместо - класса - ->
# class ImportEntity(str, Enum):
#     companies = 'companies'
#     users = 'users'


@router.post(
    '/import/{entity}/',
    summary='Универсальный массовый импорт данных через JSON или Excel файл'
)
async def universal_import(
    # FastAPI и Swagger подхватят динамический Enum
    entity: ImportEntity,  # type: ignore
    file: UploadFile = File(
        ...,
        description=(
            'Файл .json или .xlsx с валидными колонками для выбранной модели'
        )
    ),
    session: AsyncSession = Depends(get_async_session)
):
    # 2. Проверяем, зарегистрирована ли сущность в реестре (дополнительный щит)
    # берем значение из Enum через .value
    if entity.value not in SEED_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f'Сущность "{entity}" настроена в API, '
                f'но отсутствует в SEED_REGISTRY'
            )
        )

    # 3. Читаем контент файла прямо в оперативную память
    file_bytes = await file.read()

    try:
        # 4. Передаем байты и конфигурацию в наш
        # универсальный метод в seeder.py
        report = await UniversalDataSeeder.seed_memory_data(
            session=session,
            file_bytes=file_bytes,
            filename=file.filename,
            # Передаем нужный конфиг динамически
            entity_config=SEED_REGISTRY[entity.value]
        )

        # Если сидер вернул статус skipped (например, пустой файл)
        if report.get('status') == 'skipped':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=report.get(
                    'errors', ['Файл не содержит данных или пуст']
                )
            )

        return report

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Критическая ошибка сервера при импорте: {str(error)}'
        )
