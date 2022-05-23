from typing import Optional, Dict
from pydantic import BaseModel, Extra, constr


class PostProductRequest(BaseModel):
    name: constr(max_length=100)
    description: Optional[str]
    price: float


class PutProductRequest(BaseModel):
    name: Optional[constr(max_length=100)]
    description: Optional[str]
    price: Optional[float]


class ErrorModel(BaseModel):
    source: str
    type: str
    description: str


class ProductModel(BaseModel):
    name: constr(max_length=100)
    price: float
    sales: int
    description: Optional[str]
    _links: Dict[str, Dict[str, str]]
    _embedded: Dict[str, Dict[str, Dict[str, str]]]

    class Config:
        extra = Extra.allow
