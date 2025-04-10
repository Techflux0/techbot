import aiohttp
import os
from dotenv import load_dotenv
load_dotenv()

# addedd
quote = os.getenv("QUOTES")
print(F"Your chutya api key is: {quote}")
async def fetch_quote():
    url = "https://api.api-ninjas.com/v1/quotes"
    headers = {"X-Api-Key": quote}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            print(data)
            if data:
                return data[0]["quote"], data[0]["author"]
    return None, None