import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.ingestion.idempotency import idempotency_cache


@pytest.fixture(autouse=True)
def clear_cache():
    idempotency_cache.clear()


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
