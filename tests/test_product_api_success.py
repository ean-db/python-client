import pytest
from pytest_httpx import HTTPXMock

from eandb.clients.v1 import EandbV1SyncClient, EandbV1AsyncClient
from eandb.models.v1 import ProductResponse, Product

_MOCK_RESPONSES = {
    'BASIC_PRODUCT': {
        'balance': 100,
        'product': {
            'barcode': '123',
            'titles': {
                'en': 'Test'
            },
            'categories': [],
            'manufacturer': None,
            'images': [],
            'metadata': None
        }
    },
    'EXTENDED_PRODUCT': {
        'balance': 100,
        'product': {
            'barcode': '123',
            'titles': {
                'en': 'Test',
                'no': 'Tœst'
            },
            'categories': [{
                'id': '3911',
                'titles': {
                    'en': 'Bath Toys',
                    'de': 'Bad-Spielzeug'
                }
            }, {
                'id': '543543',
                'titles': {
                    'en': 'Print Books',
                    'de': 'Gedruckte Bücher'
                }
            }],
            'manufacturer': {
                'id': 'manufacturer-id',
                'titles': {
                    'en': 'Manufacturer',
                    'no': 'Manufåcturer'
                },
                'wikidataId': 'TEST'
            },
            'images': [{
                'url': 'https://ean-db.com/image.jpg'
            }],
            'metadata': {
                'externalIds': {
                    'amazonAsin': 'TEST'
                }
            }
        }
    },
    'PRODUCT_WITH_FOOD_METADATA': {
        'balance': 100,
        'product': {
            'barcode': '123',
            'titles': {
                'en': 'Test'
            },
            'categories': [],
            'manufacturer': {
                'titles': {
                    'en': 'Manufacturer'
                }
            },
            'images': [],
            'metadata': {
                'generic': {
                    'weightGrams': 100,
                    'manufacturerCode': 'TEST',
                    'color': 'blue'
                },
                'food': {
                    'nutrimentsPer100Grams': {
                        'fatGrams': 1.0,
                        'proteinsGrams': 2.0,
                        'carbohydratesGrams': 3.0,
                        'energyKCal': 4.0
                    }
                }
            }
        }
    },
    'PRODUCT_WITH_BOOK_METADATA': {
        'balance': 100,
        'product': {
            'barcode': '123',
            'titles': {
                'en': 'Test'
            },
            'categories': [],
            'manufacturer': None,
            'images': [],
            'metadata': {
                'generic': {
                    'materials': ['paper'],
                    'contributors': [{
                        'names': {
                            'en': 'John Smith'
                        },
                        'type': 'author'
                    }]
                },
                'printBook': {
                    'numPages': 123,
                    'publishedYear': 2010,
                    'bisacCodes': ['TEST'],
                    'bindingType': 'paperback'
                }
            }
        }
    },
    'PRODUCT_WITH_MUSIC_CD_METADATA': {
        'balance': 100,
        'product': {
            'barcode': '123',
            'titles': {
                'en': 'Test'
            },
            'categories': [],
            'manufacturer': None,
            'images': [],
            'metadata': {
                'musicCD': {
                    'numberOfDiscs': 2,
                    'releasedYear': 2010
                }
            }
        }
    }
}


def _set_mock(httpx_mock: HTTPXMock, mock_name: str):
    httpx_mock.add_response(status_code=200, json=_MOCK_RESPONSES.get(mock_name))


def _check_common_success(product_response: ProductResponse):
    assert isinstance(product_response, ProductResponse)
    assert product_response.error is None
    assert product_response.get_error_type() is None
    assert product_response.balance is 100


def _check_basic_product(product_response: ProductResponse):
    _check_common_success(product_response)

    assert isinstance(product_response.product, Product)
    assert product_response.product.barcode == '123'
    assert product_response.product.titles == {'en': 'Test'}
    assert product_response.product.categories == []
    assert product_response.product.manufacturer is None
    assert product_response.product.images == []
    assert product_response.product.metadata is None


def _check_extended_product(product_response: ProductResponse):
    _check_common_success(product_response)

    assert product_response.product.barcode == '123'
    assert product_response.product.titles == {'en': 'Test', 'no': 'Tœst'}
    assert isinstance(product_response.product.categories[0], Product.Category)
    assert product_response.product.categories[0].id == '3911'
    assert product_response.product.categories[0].titles == {'en': 'Bath Toys', 'de': 'Bad-Spielzeug'}
    assert product_response.product.categories[1].id == '543543'
    assert product_response.product.categories[1].titles == {'en': 'Print Books', 'de': 'Gedruckte Bücher'}
    assert isinstance(product_response.product.manufacturer, Product.Manufacturer)
    assert product_response.product.manufacturer.id == 'manufacturer-id'
    assert product_response.product.manufacturer.titles == {'en': 'Manufacturer', 'no': 'Manufåcturer'}
    assert product_response.product.manufacturer.wikidataId == 'TEST'
    assert isinstance(product_response.product.images[0], Product.Image)
    assert product_response.product.images[0].url == 'https://ean-db.com/image.jpg'
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
    assert product_response.product.metadata.generic.weightGrams == 100
    assert product_response.product.metadata.generic.manufacturerCode == 'TEST'
    assert product_response.product.metadata.generic.color == 'blue'
    assert isinstance(product_response.product.metadata.food, Product.Metadata.Food)
    assert isinstance(product_response.product.metadata.food.nutrimentsPer100Grams, Product.Metadata.Food.Nutriments)
    assert product_response.product.metadata.food.nutrimentsPer100Grams.fatGrams == 1.0
    assert product_response.product.metadata.food.nutrimentsPer100Grams.proteinsGrams == 2.0
    assert product_response.product.metadata.food.nutrimentsPer100Grams.carbohydratesGrams == 3.0
    assert product_response.product.metadata.food.nutrimentsPer100Grams.energyKCal == 4.0


def _check_product_with_book_metadata(product_response: ProductResponse):
    _check_common_success(product_response)

    assert isinstance(product_response.product.metadata, Product.Metadata)
    assert product_response.product.metadata.externalIds is None
    assert product_response.product.metadata.food is None
    assert product_response.product.metadata.musicCD is None
    assert isinstance(product_response.product.metadata.generic, Product.Metadata.Generic)
    assert product_response.product.metadata.generic.materials == ['paper']
    assert isinstance(product_response.product.metadata.generic.contributors[0], Product.Metadata.Generic.Contributor)
    assert product_response.product.metadata.generic.contributors[0].names == {'en': 'John Smith'}
    assert product_response.product.metadata.generic.contributors[0].type == 'author'
    assert isinstance(product_response.product.metadata.printBook, Product.Metadata.PrintBook)
    assert product_response.product.metadata.printBook.numPages == 123
    assert product_response.product.metadata.printBook.publishedYear == 2010
    assert product_response.product.metadata.printBook.bisacCodes == ['TEST']
    assert product_response.product.metadata.printBook.bindingType == 'paperback'


def _check_product_with_music_cd_metadata(product_response: ProductResponse):
    _check_common_success(product_response)

    assert isinstance(product_response.product.metadata, Product.Metadata)
    assert product_response.product.metadata.externalIds is None
    assert product_response.product.metadata.generic is None
    assert product_response.product.metadata.food is None
    assert product_response.product.metadata.printBook is None
    assert isinstance(product_response.product.metadata.musicCD, Product.Metadata.MusicCD)
    assert product_response.product.metadata.musicCD.numberOfDiscs == 2
    assert product_response.product.metadata.musicCD.releasedYear == 2010


def test_basic_product_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'BASIC_PRODUCT')

    with EandbV1SyncClient(jwt='TEST') as client:
        product_response = client.get_product('123')

    request = httpx_mock.get_request()

    assert request.url == 'https://ean-db.com/api/v1/product/123'
    assert request.headers['Accept'] == 'application/json'
    assert request.headers['Authorization'] == 'Bearer TEST'

    _check_basic_product(product_response)


@pytest.mark.asyncio
async def test_basic_product_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'BASIC_PRODUCT')

    async with EandbV1AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('123')

    request = httpx_mock.get_request()

    assert request.url == 'https://ean-db.com/api/v1/product/123'
    assert request.headers['Accept'] == 'application/json'
    assert request.headers['Authorization'] == 'Bearer TEST'

    _check_basic_product(product_response)


def test_extended_product_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'EXTENDED_PRODUCT')

    with EandbV1SyncClient(jwt='TEST') as client:
        product_response = client.get_product('123')

    _check_extended_product(product_response)


@pytest.mark.asyncio
async def test_extended_product_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'EXTENDED_PRODUCT')

    async with EandbV1AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('123')

    _check_extended_product(product_response)


def test_product_with_food_metadata_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'PRODUCT_WITH_FOOD_METADATA')

    with EandbV1SyncClient(jwt='TEST') as client:
        product_response = client.get_product('123')

    _check_product_with_food_metadata(product_response)


@pytest.mark.asyncio
async def test_product_with_food_metadata_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'PRODUCT_WITH_FOOD_METADATA')

    async with EandbV1AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('123')

    _check_product_with_food_metadata(product_response)


def test_product_with_book_metadata_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'PRODUCT_WITH_BOOK_METADATA')

    with EandbV1SyncClient(jwt='TEST') as client:
        product_response = client.get_product('123')

    _check_product_with_book_metadata(product_response)


@pytest.mark.asyncio
async def test_product_with_book_metadata_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'PRODUCT_WITH_BOOK_METADATA')

    async with EandbV1AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('123')

    _check_product_with_book_metadata(product_response)


def test_product_with_music_cd_metadata_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'PRODUCT_WITH_MUSIC_CD_METADATA')

    with EandbV1SyncClient(jwt='TEST') as client:
        product_response = client.get_product('123')

    _check_product_with_music_cd_metadata(product_response)


@pytest.mark.asyncio
async def test_product_with_music_cd_metadata_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, 'PRODUCT_WITH_MUSIC_CD_METADATA')

    async with EandbV1AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('123')

    _check_product_with_music_cd_metadata(product_response)
