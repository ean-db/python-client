import json
from decimal import Decimal

import pytest
from pytest_httpx import HTTPXMock

from eandb.clients.v2 import EandbV2SyncClient, EandbV2AsyncClient
from eandb.models.v2 import ProductResponse, Product

_MOCK_RESPONSES = {
    'BASIC_PRODUCT': json.load(open('tests/samples/basic.json')),
    'EXTENDED_PRODUCT': json.load(open('tests/samples/extended.json')),
    'PRODUCT_WITH_FOOD_METADATA': json.load(open('tests/samples/food.json')),
    'PRODUCT_WITH_BOOK_METADATA': json.load(open('tests/samples/book.json')),
    'PRODUCT_WITH_MUSIC_CD_METADATA': json.load(open('tests/samples/musicCD.json')),
    'PRODUCT_WITH_INGREDIENTS_METADATA': json.load(open('tests/samples/ingredients.json'))
}


def _set_mock(httpx_mock: HTTPXMock, mock_name: str):
    httpx_mock.add_response(status_code=200, json=_MOCK_RESPONSES.get(mock_name))


def _check_common_success(product_response: ProductResponse):
    assert isinstance(product_response, ProductResponse)
    assert product_response.error is None
    assert product_response.get_error_type() is None
    assert product_response.balance == 100


def _check_basic_product(product_response: ProductResponse):
    _check_common_success(product_response)

    assert isinstance(product_response.product, Product)
    assert product_response.product.barcode == '123'
    assert product_response.product.titles == {'en': 'Test'}
    assert product_response.product.categories == []
    assert product_response.product.manufacturer is None
    assert product_response.product.relatedBrands == []
    assert product_response.product.images == []
    assert product_response.product.metadata is None


def _check_extended_product(product_response: ProductResponse):
    _check_common_success(product_response)

    product = product_response.product

    assert product.barcode == '123'

    assert product.titles == {'en': 'Test', 'no': 'Tœst'}

    assert isinstance(product.categories[0], Product.Category)
    assert product.categories[0].id == '3911'
    assert product.categories[0].titles == {'en': 'Bath Toys', 'de': 'Bad-Spielzeug'}
    assert product.categories[1].id == '543543'
    assert product.categories[1].titles == {'en': 'Print Books', 'de': 'Gedruckte Bücher'}

    assert isinstance(product.manufacturer, Product.Manufacturer)
    assert product.manufacturer.id == 'manufacturer-id'
    assert product.manufacturer.titles == {'en': 'Manufacturer', 'no': 'Manufåcturer'}
    assert product.manufacturer.wikidataId == 'TEST'

    assert len(product.relatedBrands) == 1
    assert isinstance(product.relatedBrands[0], Product.Manufacturer)
    assert product.relatedBrands[0].id == 'related-brand-id'

    assert isinstance(product_response.product.images[0], Product.Image)
    assert product_response.product.images[0].url == 'https://ean-db.com/image.jpg'
    assert product_response.product.images[0].isCatalog is True

    assert isinstance(product_response.product.metadata, Product.Metadata)
    assert product_response.product.metadata.generic is None
    assert product_response.product.metadata.food is None
    assert product_response.product.metadata.printBook is None
    assert product_response.product.metadata.musicCD is None
    assert isinstance(product_response.product.metadata.externalIds, Product.Metadata.ExternalIds)
    assert product_response.product.metadata.externalIds.amazonAsin == 'TEST'


def _check_product_with_food_metadata(product_response: ProductResponse):
    _check_common_success(product_response)

    assert isinstance(product_response.product.manufacturer, Product.Manufacturer)
    assert product_response.product.manufacturer.id is None
    assert product_response.product.manufacturer.titles == {'en': 'Manufacturer'}
    assert product_response.product.manufacturer.wikidataId is None
    assert isinstance(product_response.product.metadata, Product.Metadata)
    assert product_response.product.metadata.externalIds is None
    assert product_response.product.metadata.printBook is None
    assert product_response.product.metadata.musicCD is None
    assert isinstance(product_response.product.metadata.generic, Product.Metadata.Generic)
    assert product_response.product.metadata.generic.weight.unknown is not None
    assert product_response.product.metadata.generic.weight.unknown.equals.value == 100
    assert product_response.product.metadata.generic.weight.unknown.equals.unit == 'grams'
    assert product_response.product.metadata.generic.manufacturerCode == 'TEST'
    assert product_response.product.metadata.generic.colors[0].baseColor == 'blue'
    assert isinstance(product_response.product.metadata.food, Product.Metadata.Food)
    assert isinstance(product_response.product.metadata.food.nutrimentsPer100Grams, Product.Metadata.Food.Nutriments)
    assert product_response.product.metadata.food.nutrimentsPer100Grams.fat.equals.value == 1.0
    assert product_response.product.metadata.food.nutrimentsPer100Grams.proteins.equals.value == 2.0
    assert product_response.product.metadata.food.nutrimentsPer100Grams.carbohydrates.equals.value == 3.0
    assert product_response.product.metadata.food.nutrimentsPer100Grams.energy.equals.value == 4.0
    assert product_response.product.metadata.food.nutrimentsPer100Grams.cholesterol is None
    assert product_response.product.metadata.food.nutrimentsPer100Grams.sodium is None
    assert product_response.product.metadata.food.nutrimentsPer100Grams.potassium is None
    assert product_response.product.metadata.food.nutrimentsPer100Grams.calcium.equals.value == 16.0


def _check_product_with_book_metadata(product_response: ProductResponse):
    _check_common_success(product_response)

    assert isinstance(product_response.product.metadata, Product.Metadata)
    assert product_response.product.metadata.externalIds is None
    assert product_response.product.metadata.food is None
    assert product_response.product.metadata.musicCD is None
    assert isinstance(product_response.product.metadata.generic, Product.Metadata.Generic)
    assert product_response.product.metadata.generic.ingredients[0].groupName is None
    assert product_response.product.metadata.generic.ingredients[0].ingredientsGroup[0].id == 'paper'
    assert product_response.product.metadata.generic.ingredients[0].ingredientsGroup[0].originalNames == {'en': 'Paper'}
    assert isinstance(product_response.product.metadata.generic.contributors[0], Product.Metadata.Generic.Contributor)
    assert product_response.product.metadata.generic.contributors[0].names == {'en': 'John Smith'}
    assert product_response.product.metadata.generic.contributors[0].type == 'author'
    assert isinstance(product_response.product.metadata.printBook, Product.Metadata.PrintBook)
    assert product_response.product.metadata.printBook.numPages == 123
    assert product_response.product.metadata.printBook.bisacCodes == ['TEST']
    assert product_response.product.metadata.printBook.bindingType == 'paperback'
    assert product_response.product.metadata.media.publicationYear == 2010


def _check_product_with_music_cd_metadata(product_response: ProductResponse):
    _check_common_success(product_response)

    assert isinstance(product_response.product.metadata, Product.Metadata)
    assert product_response.product.metadata.externalIds is None
    assert product_response.product.metadata.generic is None
    assert product_response.product.metadata.food is None
    assert product_response.product.metadata.printBook is None
    assert isinstance(product_response.product.metadata.musicCD, Product.Metadata.MusicCD)
    assert product_response.product.metadata.musicCD.numberOfDiscs == 2
    assert product_response.product.metadata.media.publicationYear == 2010


def _check_product_with_ingredients_metadata(product_response: ProductResponse):
    _check_common_success(product_response)

    assert isinstance(product_response.product.metadata.generic.ingredients[0], Product.Metadata.Generic.Ingredients)

    ingredients = product_response.product.metadata.generic.ingredients[0]

    assert ingredients.groupName is None
    assert len(ingredients.ingredientsGroup) == 3
    assert ingredients.ingredientsGroup[0].id is None
    assert ingredients.ingredientsGroup[0].originalNames == {'en': 'Drinking Water'}
    assert ingredients.ingredientsGroup[1].id == 'sugar'
    assert ingredients.ingredientsGroup[1].originalNames == {'en': 'Sugar'}
    assert ingredients.ingredientsGroup[1].amount.equals.value == Decimal('2.2')
    assert ingredients.ingredientsGroup[1].amount.equals.unit == 'percent'
    assert ingredients.ingredientsGroup[2].originalNames == {'en': 'Acidity Regulators'}
    assert ingredients.ingredientsGroup[2].subIngredients[0].id == 'e330'
    assert ingredients.ingredientsGroup[2].subIngredients[0].isVegan
    assert ingredients.ingredientsGroup[2].subIngredients[0].isVegetarian
    assert ingredients.ingredientsGroup[2].subIngredients[0].originalNames == {'en': 'Citric Acid'}


def test_basic_product_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'BASIC_PRODUCT')

    with EandbV2SyncClient(jwt='TEST') as client:
        product_response = client.get_product('123')

    request = httpx_mock.get_request()

    assert request.url == 'https://ean-db.com/api/v2/product/123'
    assert request.headers['Accept'] == 'application/json'
    assert request.headers['Authorization'] == 'Bearer TEST'

    _check_basic_product(product_response)


@pytest.mark.asyncio
async def test_basic_product_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'BASIC_PRODUCT')

    async with EandbV2AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('123')

    request = httpx_mock.get_request()

    assert request.url == 'https://ean-db.com/api/v2/product/123'
    assert request.headers['Accept'] == 'application/json'
    assert request.headers['Authorization'] == 'Bearer TEST'

    _check_basic_product(product_response)


def test_extended_product_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'EXTENDED_PRODUCT')

    with EandbV2SyncClient(jwt='TEST') as client:
        product_response = client.get_product('123')

    _check_extended_product(product_response)


@pytest.mark.asyncio
async def test_extended_product_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'EXTENDED_PRODUCT')

    async with EandbV2AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('123')

    _check_extended_product(product_response)


def test_product_with_food_metadata_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'PRODUCT_WITH_FOOD_METADATA')

    with EandbV2SyncClient(jwt='TEST') as client:
        product_response = client.get_product('123')

    _check_product_with_food_metadata(product_response)


@pytest.mark.asyncio
async def test_product_with_food_metadata_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'PRODUCT_WITH_FOOD_METADATA')

    async with EandbV2AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('123')

    _check_product_with_food_metadata(product_response)


def test_product_with_book_metadata_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'PRODUCT_WITH_BOOK_METADATA')

    with EandbV2SyncClient(jwt='TEST') as client:
        product_response = client.get_product('123')

    _check_product_with_book_metadata(product_response)


@pytest.mark.asyncio
async def test_product_with_book_metadata_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'PRODUCT_WITH_BOOK_METADATA')

    async with EandbV2AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('123')

    _check_product_with_book_metadata(product_response)


def test_product_with_music_cd_metadata_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'PRODUCT_WITH_MUSIC_CD_METADATA')

    with EandbV2SyncClient(jwt='TEST') as client:
        product_response = client.get_product('123')

    _check_product_with_music_cd_metadata(product_response)


@pytest.mark.asyncio
async def test_product_with_music_cd_metadata_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'PRODUCT_WITH_MUSIC_CD_METADATA')

    async with EandbV2AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('123')

    _check_product_with_music_cd_metadata(product_response)


def test_product_with_ingredients_metadata_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'PRODUCT_WITH_INGREDIENTS_METADATA')

    with EandbV2SyncClient(jwt='TEST') as client:
        product_response = client.get_product('123')

    _check_product_with_ingredients_metadata(product_response)


@pytest.mark.asyncio
async def test_product_with_ingredients_metadata_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'PRODUCT_WITH_INGREDIENTS_METADATA')

    async with EandbV2AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('123')

    _check_product_with_ingredients_metadata(product_response)
