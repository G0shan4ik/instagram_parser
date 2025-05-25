import asyncio
from pprint import pprint
from typing import Awaitable, Optional
from loguru import logger
import httpx


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class ParsBioManager:
    def __init__(self):
        self.client = None
        self.usernames: list[str] = []
        self.HEADERS = {
            "x-ig-app-id": "936619743392459",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "*/*",
        }

    async def scrape_user(self, username: str) -> str:
        try:
            logger.info(f'BIO -> {username}')
            response = await self.client.get(
                f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
            )
            response.raise_for_status()
            data = response.json()
            logger.success(f'Success pars BIO -> {username}')
            return data["data"]["user"]["biography"].replace("\n", " ")
        except Exception as ex:
            logger.error(f'scrape_user ERROR\n{ex}\n')

    async def run(self, links: list[str], per_second: int = 1, print_data: bool = False) -> Optional[dict]:
        """
            Pars Instagram BIO Manager
        :param links: [ "https://www.instagram.com/{username}?igsh={Instagram_Share_Hash}", ]
        :param per_second: Number of requests per second
        :param print_data: Output data to the console; Default False
        :return: Optional[ Dict { key(username) : value(bio text) } ]
        """
        try:
            result, _dct = [], {}
            self.usernames = [link.replace('https://www.instagram.com/', '').split("?igsh=")[0] for link in links]
            logger.info(f'Start pars bio (usernames: {self.usernames})')
            async with httpx.AsyncClient(headers=self.HEADERS) as client:
                self.client = client

                if not self.client:
                    logger.error(f'init_client ERROR\n')
                    return
                logger.success('Success init Client')

                processes: [Awaitable] = []
                for username in self.usernames:
                    processes.append(self.scrape_user(username))

                for items in chunks(processes, per_second):
                    await asyncio.sleep(2)
                    result.extend(await asyncio.gather(*items))

                for idx in range(len(self.usernames)):
                    try:
                        _dct[self.usernames[idx]] = result[idx]
                    except:
                        logger.warning('Not Found Dict Key')

                if print_data:
                    pprint(_dct)
                return _dct
        except Exception as ex:
            logger.error(f'!!! FATAL ERROR !!!\n\n{ex}\n\n')
            return {'error': str(ex)}