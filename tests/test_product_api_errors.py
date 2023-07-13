import pytest
from pytest_httpx import HTTPXMock

from eandb.clients.v1 import EandbV1SyncClient, EandbV1AsyncClient
from eandb.models.v1 import EandbResponse, ErrorType

_MOCK_RESPONSES = {
    ErrorType.INVALID_BARCODE: (
        400, {'error': {'code': 400, 'description': 'Invalid barcode: TEST'}}
    ),
    ErrorType.PRODUCT_NOT_FOUND: (
        404, {'error': {'code': 404, 'description': 'Product not found: 123'}}
    ),
    ErrorType.INVALID_JWT: (
        403, {'error': {'code': 403, 'description': 'JWT is missing or invalid, check Authorization header'}}
    ),
    ErrorType.ACCOUNT_NOT_CONFIRMED: (
        403, {
            'error': {
                'code': 403,
                'description': 'Your account is not confirmed, please check your email for confirmation link'
            }
        }
    ),
    ErrorType.JWT_REVOKED: (
        403, {'error': {'code': 403, 'description': 'JWT revoked'}}
    ),
    ErrorType.JWT_EXPIRED: (
        403, {'error': {'code': 403, 'description': 'JWT expired'}}
    ),
    ErrorType.EMPTY_BALANCE: (
        403, {'error': {'code': 403, 'description': 'Your account balance is empty'}}
    )
}


def _set_mock(httpx_mock: HTTPXMock, error_type: ErrorType):
    status_code, json = _MOCK_RESPONSES.get(error_type)
    httpx_mock.add_response(status_code=status_code, json=json)


def _check_common_error(product_response: EandbResponse, status_code: int, error_type: ErrorType):
    assert isinstance(product_response, EandbResponse)
    assert product_response.error.code == status_code
    assert product_response.get_error_type() == error_type


def _check_invalid_barcode(product_response: EandbResponse):
    _check_common_error(product_response, 400, ErrorType.INVALID_BARCODE)
    assert product_response.error.description == 'Invalid barcode: TEST'


def _check_product_not_found(product_response: EandbResponse):
    _check_common_error(product_response, 404, ErrorType.PRODUCT_NOT_FOUND)
    assert product_response.error.description == 'Product not found: 123'


def _check_invalid_jwt(product_response: EandbResponse):
    _check_common_error(product_response, 403, ErrorType.INVALID_JWT)
    assert product_response.error.description == 'JWT is missing or invalid, check Authorization header'


def _check_account_not_confirmed(product_response: EandbResponse):
    _check_common_error(product_response, 403, ErrorType.ACCOUNT_NOT_CONFIRMED)
    assert product_response.error.description == 'Your account is not confirmed, please check your email for confirmation link'


def _check_jwt_revoked(product_response: EandbResponse):
    _check_common_error(product_response, 403, ErrorType.JWT_REVOKED)
    assert product_response.error.description == 'JWT revoked'


def _check_jwt_expired(product_response: EandbResponse):
    assert product_response.get_error_type() == ErrorType.JWT_EXPIRED
    assert product_response.error.description == 'JWT expired'


def _check_empty_balance(product_response: EandbResponse):
    assert product_response.get_error_type() == ErrorType.EMPTY_BALANCE
    assert product_response.error.description == 'Your account balance is empty'


def test_400_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, ErrorType.INVALID_BARCODE)

    with EandbV1SyncClient(jwt='TEST') as client:
        product_response = client.get_product('TEST')

    _check_invalid_barcode(product_response)


@pytest.mark.asyncio
async def test_400_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, ErrorType.INVALID_BARCODE)

    async with EandbV1AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('TEST')

    _check_invalid_barcode(product_response)


def test_404_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, ErrorType.PRODUCT_NOT_FOUND)

    with EandbV1SyncClient(jwt='TEST') as client:
        product_response = client.get_product('123')

    _check_product_not_found(product_response)


@pytest.mark.asyncio
async def test_404_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, ErrorType.PRODUCT_NOT_FOUND)

    async with EandbV1AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('123')

    _check_product_not_found(product_response)


def test_403_invalid_jwt_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, ErrorType.INVALID_JWT)

    with EandbV1SyncClient(jwt='TEST') as client:
        product_response = client.get_product('123')

    _check_invalid_jwt(product_response)


@pytest.mark.asyncio
async def test_403_invalid_jwt_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, ErrorType.INVALID_JWT)

    async with EandbV1AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('123')

    _check_invalid_jwt(product_response)


def test_403_account_not_confirmed_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, ErrorType.ACCOUNT_NOT_CONFIRMED)

    with EandbV1SyncClient(jwt='TEST') as client:
        product_response = client.get_product('123')

    _check_account_not_confirmed(product_response)


@pytest.mark.asyncio
async def test_403_account_not_confirmed_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, ErrorType.ACCOUNT_NOT_CONFIRMED)

    async with EandbV1AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('123')

    _check_account_not_confirmed(product_response)


def test_403_jwt_revoked_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, ErrorType.JWT_REVOKED)

    with EandbV1SyncClient(jwt='TEST') as client:
        product_response = client.get_product('123')

    _check_jwt_revoked(product_response)


@pytest.mark.asyncio
async def test_403_jwt_revoked_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, ErrorType.JWT_REVOKED)

    async with EandbV1AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('123')

    _check_jwt_revoked(product_response)


def test_403_jwt_expired_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, ErrorType.JWT_EXPIRED)

    with EandbV1SyncClient(jwt='TEST') as client:
        product_response = client.get_product('123')

    _check_jwt_expired(product_response)


@pytest.mark.asyncio
async def test_403_jwt_expired_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, ErrorType.JWT_EXPIRED)

    async with EandbV1AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('123')

    _check_jwt_expired(product_response)


def test_403_empty_balance_sync(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, ErrorType.EMPTY_BALANCE)

    with EandbV1SyncClient(jwt='TEST') as client:
        product_response = client.get_product('123')

    _check_empty_balance(product_response)


@pytest.mark.asyncio
async def test_403_empty_balance_async(httpx_mock: HTTPXMock):
    _set_mock(httpx_mock, ErrorType.EMPTY_BALANCE)

    async with EandbV1AsyncClient(jwt='TEST') as client:
        product_response = await client.get_product('123')

    _check_empty_balance(product_response)
