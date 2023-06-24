import abc

import httpx

from eandb.models.v1 import ProductResponse, EandbResponse


class EandbV1AbstractClient(abc.ABC):
    DEFAULT_BASE_URL = 'https://ean-db.com'
    PRODUCT_ENDPOINT = '/api/v1/product/{barcode}'

    def __init__(self, *, jwt: str = ''):
        if not jwt:
            raise ValueError(f'`jwt` param is empty')

        self.jwt = jwt

    def _process_product_response(self, response: httpx.Response) -> ProductResponse | EandbResponse:
        if response.status_code == httpx.codes.OK:
            return ProductResponse.parse_obj(response.json())

        if response.status_code in (httpx.codes.NOT_FOUND, httpx.codes.FORBIDDEN, httpx.codes.BAD_REQUEST):
            return EandbResponse.parse_obj(response.json())

        response.raise_for_status()


class EandbV1SyncClient(EandbV1AbstractClient):
    def __init__(self, *, jwt: str = '', **kwargs):
        super().__init__(jwt=jwt)

        default_headers = {'Authorization': f'Bearer {jwt}', 'Accept': 'application/json'}

        self.client = httpx.Client(
            headers=kwargs.get('headers', default_headers),
            base_url=kwargs.get('base_url', self.DEFAULT_BASE_URL),
            **kwargs
        )

    def get_product(self, barcode: str) -> ProductResponse | EandbResponse:
        response = self.client.get(self.PRODUCT_ENDPOINT.format(barcode=barcode))

        print(response.request.headers)
        return self._process_product_response(response)

    def close(self):
        self.client.close()

    def __enter__(self):
        self.client.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.__exit__(exc_type, exc_val, exc_tb)


class EandbV1AsyncClient(EandbV1AbstractClient):
    def __init__(self, *, jwt: str = '', **kwargs):
        super().__init__(jwt=jwt)

        default_headers = {'Authorization': f'Bearer {jwt}', 'Accept': 'application/json'}

        self.client = httpx.AsyncClient(
            headers=kwargs.get('headers', default_headers),
            base_url=kwargs.get('base_url', self.DEFAULT_BASE_URL),
            **kwargs
        )

    async def get_product(self, barcode: str) -> ProductResponse | EandbResponse:
        response = await self.client.get(self.PRODUCT_ENDPOINT.format(barcode=barcode))
        return self._process_product_response(response)

    async def aclose(self):
        await self.client.aclose()

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)