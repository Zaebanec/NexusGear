# src/presentation/web/api/schemas/category.py

from pydantic import BaseModel, ConfigDict

class CategorySchema(BaseModel):
    """
    Схема для отображения данных о категории в API.
    """
    id: int
    name: str

    # Эта конфигурация позволяет Pydantic читать данные
    # напрямую из SQLAlchemy-объектов (orm_mode).
    model_config = ConfigDict(from_attributes=True)