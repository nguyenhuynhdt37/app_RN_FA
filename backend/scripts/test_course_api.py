import asyncio
import httpx
import json
from uuid import UUID

BASE_URL = "http://localhost:8000/api/v1"

async def test_get_courses():
    async with httpx.AsyncClient() as client:
        print("\n--- Testing GET /courses ---")
        try:
            # 1. Test basic list
            response = await client.get(f"{BASE_URL}/courses?page=1&page_size=5")
            print(f"Basic List Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Total items: {data.get('total')}")
                print(f"Items on page: {len(data.get('items', []))}")
                if data.get('items'):
                    print(f"First item title: {data['items'][0].get('title')}")
            
            # 2. Test search
            search_term = "React"
            response = await client.get(f"{BASE_URL}/courses?search={search_term}")
            print(f"\nSearch '{search_term}' Status: {response.status_code}")
            
            # 3. Test sorting
            sort_options = ["newest", "popular", "rating", "price_asc", "price_desc"]
            for sort in sort_options:
                response = await client.get(f"{BASE_URL}/courses?sort={sort}")
                print(f"Sort '{sort}' Status: {response.status_code}")

            # 4. Test lang fallback
            response = await client.get(f"{BASE_URL}/courses?lang=en")
            print(f"\nLang 'en' Status: {response.status_code}")

        except Exception as e:
            print(f"Error connecting to API: {e}")
            print("Make sure the backend is running on http://localhost:8000")

if __name__ == "__main__":
    asyncio.run(test_get_courses())
