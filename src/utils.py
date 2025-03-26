import asyncio
import aiohttp
from io import BytesIO
from PIL import Image
from typing import Literal

def debug_message(message, type: Literal['debug', 'error'] = 'debug'):
    from config import DEBUG
    if DEBUG:
        if type == 'debug':
            print(f"\033[34m[DEBUG] {message}\033[37m")
        elif type == 'error':
            print(f"\033[31m [ERROR] {message}\033[37m")
            quit()  ### Maybe this will mean return to search in the future

async def fetch_image(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            img_data = await response.read()
            return BytesIO(img_data)  # Keep image in memory
        else:
            debug_message(f"Failed to fetch {url} - Status: {response.status}")
            return None
        
async def download_pack_images(image_urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_image(session, url) for url in image_urls]
        return await asyncio.gather(*tasks)  # Fetch all images concurrently
