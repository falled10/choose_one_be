import httpx

from core.settings import RECOMMENDATION_SERVICE_URL


async def get_user_recommendations(user_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{RECOMMENDATION_SERVICE_URL}/api/recommendation/{user_id}",
                                headers={'Content-Type': 'application/json'})
    return resp.json()