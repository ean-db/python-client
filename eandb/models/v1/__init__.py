import enum
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ErrorType(enum.Enum):
    INVALID_BARCODE = enum.auto()
    PRODUCT_NOT_FOUND = enum.auto()
    INVALID_JWT = enum.auto()
    ACCOUNT_NOT_CONFIRMED = enum.auto()
    JWT_REVOKED = enum.auto()
    JWT_EXPIRED = enum.auto()
    EMPTY_BALANCE = enum.auto()


_ERROR_MESSAGE_TO_CODE = {
    'Product not found: ': ErrorType.PRODUCT_NOT_FOUND,
    'JWT is missing or invalid, check Authorization header': ErrorType.INVALID_JWT,
    'Your account is not confirmed': ErrorType.ACCOUNT_NOT_CONFIRMED,
    'JWT revoked': ErrorType.JWT_REVOKED,
    'JWT expired': ErrorType.JWT_EXPIRED,
    'Your account balance is empty': ErrorType.EMPTY_BALANCE
}


class Error(BaseModel):
    code: int
    description: str


class EandbResponse(BaseModel):
    balance: Optional[int]
    error: Optional[Error]

    def get_error_type(self) -> Optional[ErrorType]:
        if not self.error:
            return None

        if self.error.code == 400:
            return ErrorType.INVALID_BARCODE

        for msg, code in _ERROR_MESSAGE_TO_CODE.items():
            if self.error.description.startswith(msg):
                return code

        return None


class Product(BaseModel):
    class Category(BaseModel):
        id: str
        titles: dict[str, str]

    class Manufacturer(BaseModel):
        id: Optional[str]
        titles: dict[str, str]
        wikidataId: Optional[str]

    class Image(BaseModel):
        url: str

    class Metadata(BaseModel):
        class ExternalIds(BaseModel):
            amazonAsin: Optional[str]

        class Generic(BaseModel):
            class Contributor(BaseModel):
                names: dict[str, str]
                type: str

            weightGrams: Optional[int]
            manufacturerCode: Optional[str]
            color: Optional[str]
            materials: Optional[list[str]]
            contributors: Optional[list[Contributor]]

        class Food(BaseModel):
            class Nutriments(BaseModel):
                fatGrams: Optional[Decimal]
                proteinsGrams: Optional[Decimal]
                carbohydratesGrams: Optional[Decimal]
                energyKCal: Optional[Decimal]

            nutrimentsPer100Grams: Optional[Nutriments]

        class PrintBook(BaseModel):
            numPages: Optional[int]
            publishedYear: Optional[int]
            bisacCodes: Optional[list[str]]
            bindingType: Optional[str]

        class MusicCD(BaseModel):
            releasedYear: Optional[int]
            numberOfDiscs: Optional[int]

        externalIds: Optional[ExternalIds]
        generic: Optional[Generic]
        food: Optional[Food]
        printBook: Optional[PrintBook]
        musicCD: Optional[MusicCD]

    barcode: str
    titles: dict[str, str]
    categories: list[Category]
    manufacturer: Optional[Manufacturer]
    images: list[Image]
    metadata: Optional[Metadata]


class ProductResponse(EandbResponse):
    product: Product
