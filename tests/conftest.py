import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from src.config import settings
from src.main import app
from src.ingestion.idempotency import idempotency_cache
from src.notion.client import notion_client


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Ensure tests run in isolated Mock Mode."""
    idempotency_cache.clear()
    settings.MOCK_NOTION = True
    settings.MOCK_EMAIL = True
    notion_client.mock_mode = True


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
