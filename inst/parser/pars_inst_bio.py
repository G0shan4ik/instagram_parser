import asyncio
import random
import re
from pprint import pprint
from typing import Optional, Awaitable, List, Dict
from concurrent.futures import ThreadPoolExecutor

import instaloader
from loguru import logger


def chunks(lst, n):
    """Разбивает список на чанки по n элементов."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class ParsBioManager:
    @staticmethod
    async def safe_sleep(min_seconds=1.5, max_seconds=3.0, print_sec: bool = False) -> None:
        duration = random.uniform(min_seconds, max_seconds)
        if print_sec:
            logger.info(f"Sleep for: {duration:.2f} sec")
        await asyncio.sleep(duration)

    def scrape_bio(self, username: str) -> Dict[str, str]:
        try:
            loader = instaloader.Instaloader()
            loader.context.log("Работаем без авторизации — возможен ограниченный доступ")

            profile = instaloader.Profile.from_username(loader.context, username)
            bio = profile.biography.replace("\n", " ").strip()

            logger.success(f'Success: {username}')
            return {username: bio}
        except Exception as ex:
            logger.error(f'Error while scraping bio for {username}: {ex}')
            return {username: f"error: {str(ex)}"}

    async def async_parse_instagram_bio(self, username: str) -> Dict[str, str]:
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            result: Dict[str, str] = await loop.run_in_executor(pool, self.scrape_bio, username)
            return result

    async def run(self, links: List[str], per_second: int = 1, print_data: bool = False) -> Optional[List[Dict[str, str]]]:
        """
        Pars Instagram BIO Manager

        :param links: Список ссылок на Instagram-профили
        :param per_second: Количество запросов за раз (чанк)
        :param print_data: Вывод результата в консоль
        :return: Список словарей {username: biography}
        """
        try:
            usernames = []
            for link in links:
                match = re.match(r"https?://www\.instagram\.com/([^/?#]+)/?", link)
                if match:
                    usernames.append(match.group(1))
                else:
                    logger.warning(f"Не удалось извлечь username из ссылки: {link}")

            logger.info(f'Start parsing usernames: {usernames}')

            processes: List[Awaitable] = []
            result: List[Dict[str, str]] = []

            for username in usernames:
                processes.append(self.async_parse_instagram_bio(username))

            for batch in chunks(processes, per_second):
                result.extend(await asyncio.gather(*batch))
                await self.safe_sleep(print_sec=print_data)

            if print_data:
                pprint(result)
            return result
        except Exception as ex:
            logger.error(f'FATAL ERROR\n\n{ex}\n')
            return [{'error': str(ex)}]
