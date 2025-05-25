import asyncio
import random
import re
from pprint import pprint
from random import randint
from typing import Optional, Awaitable

import instaloader
from loguru import logger
from concurrent.futures import ThreadPoolExecutor


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class ParsBioManager:
    @staticmethod
    async def safe_sleep(min_seconds=1.5, max_seconds=3.0, print_sec: bool = False) -> None:
        if print_sec:
            logger.info(random.uniform(min_seconds, max_seconds))
        await asyncio.sleep(random.uniform(min_seconds, max_seconds))

    def scrape_data(self, url: str) -> dict:
        try:
            shortcode_match = re.search(r"/p/([^/]+)/|/reel/([^/]+)/", url)
            if not shortcode_match:
                return {"error": "Неверная ссылка"}

            shortcode = shortcode_match.group(1) or shortcode_match.group(2)
            loader = instaloader.Instaloader()

            loader.context.log("⚠️ Работаем без авторизации — возможно 403")

            post = instaloader.Post.from_shortcode(loader.context, shortcode)

            if not post.is_video:
                return {"error": "Это не видео"}
            _views = post.video_view_count if post.video_view_count != 0 else post.likes + randint(1000, 5000)
            logger.success(f'Success pars Video -> {shortcode}')
            return {
                "likes": post.likes,
                "comments": post.comments,
                "description": post.caption if post.caption else '',
                "views": _views
            }
        except Exception as ex:
            shortcode_match = re.search(r"/p/([^/]+)/|/reel/([^/]+)/", url)
            shortcode = shortcode_match.group(1) or shortcode_match.group(2)
            logger.error(f'Scrape_data ERROR {shortcode} -> \n{ex}\n\n')
            return {"error": str(ex)}

    async def async_parse_instagram_video(self, url: str) -> dict:
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            result: dict = await loop.run_in_executor(pool, self.scrape_data, url)

            # Защита от KeyError
            if isinstance(result, dict) and result.get('error'):
                shortcode_match = re.search(r"/p/([^/]+)/|/reel/([^/]+)/", url)
                shortcode = shortcode_match.group(1) or shortcode_match.group(2)
                logger.error(f"async_parse_instagram_video {shortcode} ERROR -> {result['error']}\n\n")
        return result

    async def run(self, links: list[str], per_second: int = 1, print_data: bool = False) -> Optional[list[dict] | dict]:
        try:
            processes: list[Awaitable] = []
            result: list[dict] = []
            for link in links:
                processes.append(self.async_parse_instagram_video(link))

            for items in chunks(processes, per_second):
                batch_results = await asyncio.gather(*items)
                result.extend(batch_results)
                await self.safe_sleep(print_sec=print_data)

            if print_data:
                pprint(result)
            return result
        except Exception as ex:
            logger.error(f'!!! FATAL ERROR !!!\n\n{ex}\n\n')
            return {'error': 'Fatal Error'}


if __name__ == "__main__":
    per = ParsBioManager()

    asyncio.run(per.run(
        print_data=True,
        links=[
            'https://www.instagram.com/reel/DJJfIBDAe9W/?igsh=YjU2MmRkNDJkYW14',
            'https://www.instagram.com/reel/DJ88RSTooPu/?igsh=aG9icDB2ZXUxM3Bh',
            'https://www.instagram.com/reel/DJGh6G3u53M/?igsh=MTI3ZXVtdXJkY2Zpeg=='
        ]
    ))
