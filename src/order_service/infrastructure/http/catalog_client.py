import httpx

from order_service.application.ports.catalog_client import CatalogClient, CatalogItem
from order_service.domain.exceptions import ItemNotAvailableError


class HttpCatalogClient(CatalogClient):
    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url
        self._api_key = api_key
        self._client = httpx.AsyncClient(timeout=10.0)

    async def get_item(self, item_id: str) -> CatalogItem:
        response = await self._client.get(
            f"{self._base_url}/api/catalog/items/{item_id}/",
            headers={"X-API-Key": self._api_key},
        )
        if response.status_code == 404:
            raise ItemNotAvailableError
        response.raise_for_status()
        return CatalogItem(**response.json())

    async def close(self):
        await self._client.aclose()
