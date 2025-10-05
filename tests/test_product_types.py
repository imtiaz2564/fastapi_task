# import pytest
#
# @pytest.fixture
# def jwt_token(client):
#     client.post("/auth/register", json={"username": "ptype", "password": "ptypepass"})
#     res = client.post("/auth/login", json={"username": "ptype", "password": "ptypepass"})
#     return res.json()["access_token"]
#
# def test_create_product_type(client, jwt_token):
#     res = client.post(
#         "/product-types/",
#         headers={"Authorization": f"Bearer {jwt_token}"},
#         json={"name": "Electronics", "description": "Devices"},
#     )
#     assert res.status_code in [200, 201]
#     assert res.json()["name"] == "Electronics"
#
# def test_update_product_type(client, jwt_token):
#     res = client.post(
#         "/product-types/",
#         headers={"Authorization": f"Bearer {jwt_token}"},
#         json={"name": "Furniture", "description": "Home items"},
#     )
#     pt_id = res.json()["id"]
#
#     res = client.put(
#         f"/product-types/{pt_id}",
#         headers={"Authorization": f"Bearer {jwt_token}"},
#         json={"name": "Office Furniture", "description": "Desks and chairs"},
#     )
#     assert res.status_code == 200
#     assert res.json()["name"] == "Office Furniture"
#
# def test_delete_product_type(client, jwt_token):
#     res = client.post(
#         "/product-types/",
#         headers={"Authorization": f"Bearer {jwt_token}"},
#         json={"name": "Temporary", "description": "To be deleted"},
#     )
#     pt_id = res.json()["id"]
#
#     res = client.delete(
#         f"/product-types/{pt_id}",
#         headers={"Authorization": f"Bearer {jwt_token}"},
#     )
#     assert res.status_code in [200, 204]
#
#     res = client.get(f"/product-types/{pt_id}")
#     assert res.status_code in [404, 400]
import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager
from app.main import app
from app.database import engine, Base


# --- DB RESET FIXTURE ---
# @pytest.fixture(scope="function", autouse=True)
# async def reset_db():
#     """Drop and recreate all tables before each test."""
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#     yield


# --- CREATE ---
@pytest.mark.asyncio
async def test_create_product_type():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            name = f"Type_{uuid.uuid4().hex[:6]}"
            res = await client.post("/product-types/", json={"name": name, "description": "Some description"})
            print("CREATE:", res.text)
            assert res.status_code in (200, 201)
            data = res.json()
            assert data["name"] == name


# --- READ ALL ---
@pytest.mark.asyncio
async def test_get_all_product_types():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # First, create one product type
            name = f"Type_{uuid.uuid4().hex[:6]}"
            await client.post("/product-types/", json={"name": name, "description": "Desc"})

            res = await client.get("/product-types/")
            print("GET ALL:", res.text)
            assert res.status_code == 200
            data = res.json()
            assert isinstance(data, list)
            assert any(pt["name"] == name for pt in data)


# --- READ ONE ---
@pytest.mark.asyncio
async def test_get_single_product_type():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            name = f"Type_{uuid.uuid4().hex[:6]}"
            res = await client.post("/product-types/", json={"name": name, "description": "Desc"})
            pt_id = res.json()["id"]

            res = await client.get(f"/product-types/{pt_id}")
            print("GET SINGLE:", res.text)
            assert res.status_code == 200
            assert res.json()["name"] == name


# --- UPDATE ---
@pytest.mark.asyncio
async def test_update_product_type():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            name = f"Type_{uuid.uuid4().hex[:6]}"
            res = await client.post("/product-types/", json={"name": name, "description": "Old"})
            pt_id = res.json()["id"]

            updated_name = f"{name}_Updated"
            res = await client.put(f"/product-types/{pt_id}", json={"name": updated_name, "description": "New"})
            print("UPDATE:", res.text)
            assert res.status_code == 200
            assert res.json()["name"] == updated_name


# --- DELETE ---
@pytest.mark.asyncio
async def test_delete_product_type():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            name = f"Type_{uuid.uuid4().hex[:6]}"
            res = await client.post("/product-types/", json={"name": name, "description": "Desc"})
            pt_id = res.json()["id"]

            res = await client.delete(f"/product-types/{pt_id}")
            print("DELETE:", res.text)
            assert res.status_code == 200
            assert res.json()["detail"] == "Product type deleted"
