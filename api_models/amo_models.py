import asyncio
import logging
from pprint import pprint

import aiohttp

from config_reader import config
from sql import SQLiteDB


logger = logging.getLogger('AMOCrm_API')


class AMO:
    def __init__(self, access_token: str, refresh_token: str):
        self.client_id = config.client_id.get_secret_value()
        self.client_secret = config.client_secret.get_secret_value()
        self.redirect_uri = config.redirect_uri.get_secret_value()

        self.access_token = access_token
        self.refresh_token = refresh_token

        self.subdomain = config.subdomain.get_secret_value()
        self.api_link = f'{self.subdomain}api/v4/'
        self.headers = {
            "Authorization": "Bearer " + self.access_token if self.access_token else ''
        }

    async def get_access_token_first_time(self) -> tuple:
        async with aiohttp.ClientSession() as session:
            code = input("Токены не найдены, требуется авторизация. Введите авторизационный код интеграции: ")
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.redirect_uri
            }
            async with session.post(url=f'{self.subdomain}oauth2/access_token', data=data) as response:
                result = await response.json()
                if result.get('access_token') and result.get('refresh_token'):
                    await SQLiteDB().update_access_data(access_token=result['access_token'],
                                                        refresh_token=result['refresh_token'])
                    self.access_token = result.get('access_token')
                    self.refresh_token = result.get('refresh_token')
                    logger.info(f'Received new access and refresh tokens')
                    return result['access_token'], result['refresh_token']
                else:
                    print(f'{result["status"]} Неудачная попытка получения токенов. Проверьте введенные данные.')
                    await self.get_access_token_first_time()

    async def get_new_access_token(self) -> tuple:
        async with aiohttp.ClientSession() as session:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'redirect_uri': self.redirect_uri
            }
            async with session.post(url=f'{self.subdomain}oauth2/access_token', data=data) as response:
                result = await response.json()
                await SQLiteDB().update_access_data(access_token=result['access_token'],
                                                    refresh_token=result['refresh_token'])
                self.access_token = result.get('access_token')
                self.refresh_token = result.get('refresh_token')
                logger.info(f'Received new access and refresh tokens')
                return result['access_token'], result['refresh_token']

    async def __post(self, method: str, data: dict = None) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.api_link}{method}', json=data, headers=self.headers) as response:
                return await response.json()

    async def __get(self, method: str, params: dict = None) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.api_link}{method}', headers=self.headers, params=params) as response:
                return await response.json()

    async def get_custom_fields(self) -> list:
        result, requests_counter = [], 0
        for group in ['leads', 'contacts', 'companies']:
            method = f'{group}/custom_fields'
            fields_data = await self.__get(method=method)
            requests_counter += 1
            await asyncio.sleep(0.5)
            result += fields_data['_embedded']['custom_fields']
            if fields_data['_page_count'] > 1:
                for i in range(2, fields_data['_page_count'] + 1):
                    fields_data = await self.__get(method=method, params={'page': i})
                    requests_counter += 1
                    await asyncio.sleep(0.5)
                    result += fields_data['_embedded']['custom_fields']
        logger.info(f'Received {len(result)-4} custom fields, {requests_counter} requests made')
        return result

    async def get_group_name(self, group_id: str) -> str:
        entity = group_id.split('_')[0]
        method = f'{entity}/custom_fields/groups/{group_id}'
        group_data = await self.__get(method=method)
        return group_data.get('name')
