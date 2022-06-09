from flask import Request

from typing import Optional, Dict
from pydantic import BaseModel, constr, Field

from db.db import Products, Reviews, Orders


class PostProduct(BaseModel):
    name: constr(max_length=100)
    description: Optional[str]
    price: float


class PutProduct(BaseModel):
    name: Optional[constr(max_length=100)]
    description: Optional[str]
    price: Optional[float]


class PostBaseReview(BaseModel):
    rating: int
    text: Optional[str]


class ErrorModel(BaseModel):
    source: str
    type: str
    description: str


class ProductModel(BaseModel):
    name: constr(max_length=100)
    price: float
    sales: int
    description: Optional[str]
    links: Dict[str, Dict[str, str]] = Field(alias='_links')
    embedded: Optional[
        Dict[str, Dict[str, Dict[str, str]]]
    ] = Field(alias='_embedded')

    @staticmethod
    def create(product: Products, request: Request) -> 'ProductModel':
        """Creates ProductModel object from product and flask request

        Args:
            product (Products): database product object.
            request (Request): flask request object.

        Returns:
            ProductModel: pydantic model object.
        """
        item = ProductModel(
            name=product.name,
            price=product.price,
            sales=product.sales,
            _links=dict(
                self=dict(
                    href=(request.root_url +
                          f'api/v1/products/{product.name}')
                ),
                reviews=dict(
                    href=(request.url_root +
                          f'api/v1/products/{product.name}/reviews')
                ),
                orders=dict(
                    href=(request.url_root +
                          f'api/v1/products/{product.name}/orders')
                )
            ),
            _embedded=dict(
                image=dict(
                    _links=dict(
                        self=(request.root_url +
                              product.image_url[1:])
                    )
                )
            )
        )

        if product.description:
            item.description = product.description
        return item


class ReviewModel(BaseModel):
    text: Optional[str]
    rating: int
    links: Dict[str, Dict[str, str]] = Field(alias='_links')
    embedded: Optional[
        Dict[str, Dict[str, Dict[str, str]]]
    ] = Field(alias='_embedded')

    @staticmethod
    def create(review: Reviews, request: Request) -> 'ReviewModel':
        item = ReviewModel(
            rating=review.rating,
            _links=dict(
                self=dict(
                    href=request.url
                ),
                owner=dict(
                    href=(request.root_url +
                          f'api/v1/users/{review.owner_id}')
                ),
                product=dict(
                    href=(request.root_url +
                          f'api/v1/products/{review.product.name}')
                )
            )
        )

        if review.text:
            item.text = review.text
        if review.image_url:
            item.embedded = dict(
                image=dict(
                    _links=dict(
                        self=(request.root_url +
                              review.image_url[1:])
                    )
                )
            )

        return item


class OrderModel(BaseModel):
    address: constr(max_length=100)
    wishes: Optional[str]
    created_at_utc: str
    status: constr(max_length=50)
    links: Dict[str, Dict[str, str]] = Field(alias='_links')

    @staticmethod
    def create(request: Request, order: Orders) -> 'OrderModel':
        item = OrderModel(
            address=order.address,
            created_at_utc=order.created,
            status=order.status,
            _links=dict(
                self=dict(
                    href=(request.root_url +
                          f'api/v1/orders/{order.id}')
                ),
                product=dict(
                    href=(request.root_url +
                          f'api/v1/products/{order.product.name}')
                ),
                owner=dict(
                    href=(request.root_url +
                          f'api/v1/users/{order.owner_id}')
                )
            )
        )

        if order.wishes:
            item.wishes = order.wishes

        return item
