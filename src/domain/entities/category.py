from dataclasses import dataclass


@dataclass
class Category:
    """
    Доменная сущность 'Категория'.

    Представляет категорию, к которой может принадлежать товар.
    """
    id: int
    name: str