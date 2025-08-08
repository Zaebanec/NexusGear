# src/presentation/web/api/schemas/product.py

from pydantic import BaseModel, ConfigDict

class ProductSchema(BaseModel):
    """
    Схема для отображения данных о товаре в API.
    """
    id: int
    name: str
    price: float
    category_id: int

    model_config = ConfigDict(from_attributes=True)