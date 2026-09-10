# data seeding (засев базы данных) - автоматическое
# наполнение базы тестовыми данными.
# делаем универсальный инструмент, который будет читать и JSON, и
# файлы Excel (.xlsx), а затем через BaseCRUD закидывать всё в Postgres.

# Шаг 1
# чтобы Python умел читать файлы .xlsx, ставим библиотеку openpyxl>=3.1.0
# Шаг 2
# делаем новую директорию для тестовых данных:app/seeds/
# в ней - папки по моделям, куда кидаем файлы типа json и xlsx. Будем
# грузить их все, исключая дубликаты и кривые строки
# Шаг 3
# Тут - оформляем парсер-заселитель/
# По размышлению - решил объединить:
# -- Дисковый сидер (из папок seeds/json) нужен для разработчика.
# Когда делаем docker-compose down -v, сносишь базу и поднимаешь её заново,
# этот сидер автоматически закидывает в базу базовых системных пользователей,
# типы тарифов или тестовые компании, чтобы проект сразу стартовал «живым».
# -- Веб-сидер (из памяти через роутер) нужен для администратора (для
# пользователя системы). Он работает интерактивно в процессе жизни приложения,
# когда админу нужно раз в месяц массово импортировать 500 новых клиентов
# из Excel.

# app/core/seeder.py
import json
import os
from io import BytesIO
from typing import Any, Dict, List
from openpyxl import load_workbook
from sqlalchemy.ext.asyncio import AsyncSession
from app.seeds.registry import SEED_REGISTRY
from app.core.config import settings


class UniversalDataSeeder:
    @classmethod
    def parse_memory_file(
        cls, file_bytes: bytes, filename: str
    ) -> list[dict[str, Any]]:
        """
        Парсит файл, загруженный в оперативную память.
        (без сохранения на диск)
        """
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        if ext == '.json':
            return json.loads(file_bytes.decode('utf-8'))
        elif ext == '.xlsx':
            # Заворачиваем байты в поток BytesIO,
            # чтобы openpyxl мог его прочитать
            return cls._parse_excel(BytesIO(file_bytes))

        raise ValueError(
            'Неподдерживаемый формат файла. '
            'Разрешены только .json и .xlsx'
        )

    @staticmethod
    def _parse_excel(stream: Any) -> List[Dict[str, Any]]:
        wb = load_workbook(stream, data_only=True)
        sheet = wb.active

        # извлекаем первую строку с заголовками
        first_row = next(sheet.iter_rows(max_row=1))
        headers = [cell.value for cell in first_row if cell.value is not None]

        result = []
        # читаем данные, начиная со второй строки (min_row=2)
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not any(row):  # Пропускаем пустые строки
                continue
            # Склеиваем заголовки со значениями ячеек
            row_dict = dict(zip(headers, row))
            result.append(row_dict)
        return result

    @classmethod
    def _load_file_data(cls, file_path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(file_path):
            return []
        _, ext = os.path.splitext(file_path)
        if ext.lower() == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif ext.lower() == '.xlsx':
            with open(file_path, 'rb') as f:
                return cls._parse_excel(f)
        return []

    @classmethod
    async def seed_memory_data(
        cls,
        session: AsyncSession,
        file_bytes: bytes,
        filename: str,
        entity_config: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Универсальный движок для импорта данных из памяти.
        Принимает байты файла, имя файла и конфигурацию сущности из реестра.
        """
        # Парсим файл в список словарей
        raw_data = cls.parse_memory_file(file_bytes, filename)

        if not raw_data:
            return {
                'status': 'skipped',
                'created': 0,
                'skipped_duplicates': 0,
                'errors': ['Файл пуст']
            }

        created_count = 0
        skipped_count = 0
        errors = []

        crud = entity_config['crud']
        schema = entity_config['schema']
        unique_field = entity_config['unique_field']

        # Бежим по строкам точно так же, как в автоматическом сидере
        for index, item in enumerate(raw_data, start=1):
            try:
                unique_value = item.get(
                    unique_field
                ) or item.get('inn') or item.get('email')

                if unique_value is not None:
                    unique_value = str(unique_value).strip()
                    filters = {unique_field: unique_value}
                    exists = await crud.find_one_or_none(session, **filters)
                    if exists:
                        skipped_count += 1
                        continue

                validated_obj = schema(**item)
                await crud.create(session, obj_in=validated_obj)
                created_count += 1

            except Exception as error_message:
                errors.append(f'Строка {index}: {str(error_message)}')

        return {
            'status': 'success' if not errors else 'partial_success',
            'imported_new_records': created_count,
            'skipped_duplicates': skipped_count,
            'errors': errors
        }

    @classmethod
    async def seed_all(cls, session: AsyncSession) -> None:
        """Динамически обходит все папки из реестра и засевает базу"""

        # берем путь из settings
        base_dir = settings.SEEDS_DIR

        if not os.path.exists(base_dir):
            os.makedirs(base_dir, exist_ok=True)
            print(
                f'⚠️ Папка для автозасева [{base_dir}] не найдена. '
                f'Создана пустая.'
            )
            return

        for entity_name, config in SEED_REGISTRY.items():
            entity_folder = os.path.join(base_dir, entity_name)

            if not os.path.exists(entity_folder):
                continue  # папка модели не создана — пропускаем

            # Получаем список вообще всех файлов в этой папке
            files = os.listdir(entity_folder)

            # Заводим счетчики для итогового отчета по модели
            total_created = 0
            total_skipped = 0

            # target_file = None
            # Бежим по всем файлам в папке сущности
            for file in files:
                if not file.endswith(('.json', '.xlsx')):
                    continue  # Пропускаем левые файлы (txt, скрытые)

                target_file = os.path.join(entity_folder, file)
                # Читаем данные из текущего файла (JSON или Excel)
                raw_data = cls._load_file_data(target_file)
                if not raw_data:
                    continue

                print(
                    f'🌱 [Seeder] Найдено {len(raw_data)} строк в файле: '
                    f'{file}. Начинаю импорт...'
                )

                crud = config['crud']
                schema = config['schema']
                unique_field = config['unique_field']

                # проходим по строкам конкретного файла
                for index, item in enumerate(raw_data, start=1):
                    try:
                        unique_value = item.get(unique_field)
                        if unique_value is not None:
                            unique_value = str(unique_value).strip()
                            filters = {unique_field: unique_value}
                            exists = await crud.find_one_or_none(
                                session, **filters
                            )
                            if exists:
                                total_skipped += 1
                                # Запись уже есть в базе — пропускаем строчку
                                continue

                        # Валидируем и создаем запись
                        validated_obj = schema(**item)
                        await crud.create(session, obj_in=validated_obj)
                        total_created += 1

                    except Exception as error_message:
                        print(
                            f'❌ [{entity_name}] Ошибка в файле {file} '
                            f'на строке {index}: {error_message}. '
                            f'Строка пропущена.'
                        )
                        continue

            # Выводим красивый суммарный итог по завершении
            # обработки всей папки
            if total_created > 0 or total_skipped > 0:
                print(
                    f'🏁 [Seeder] Завершен импорт для [{entity_name}]. '
                    f'Добавлено новых записей: {total_created}, '
                    f'пропущено дубликатов: {total_skipped}'
                )
