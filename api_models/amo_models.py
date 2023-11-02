import asyncio
from pprint import pprint

import aiohttp


class AMO:
    def __init__(self):
        self.client_id = '7be7043c-7d17-4007-af93-09816ed7dc4c'
        self.client_secret = 'COTKpWyo5fvozfOWQJ75F8kUgLgGKRxCA1bJN09OViIMpSWQbUoMzOTkI0FvPxCB'
        self.redirect_uri = 'https://somesite.com:9999'

        self.access_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjEyZDMzYmE5ZGI4Y2FmZDNiODVjMjg5NTE0NTBhMWIyYTI3YWI3MmFlMjhkYjk0MDNhMGYwOWRhYTg5OWVlNGI0MjgwMmI0ZjI2YTVmMmU5In0.eyJhdWQiOiI3YmU3MDQzYy03ZDE3LTQwMDctYWY5My0wOTgxNmVkN2RjNGMiLCJqdGkiOiIxMmQzM2JhOWRiOGNhZmQzYjg1YzI4OTUxNDUwYTFiMmEyN2FiNzJhZTI4ZGI5NDAzYTBmMDlkYWE4OTllZTRiNDI4MDJiNGYyNmE1ZjJlOSIsImlhdCI6MTY5ODkyNDkwNCwibmJmIjoxNjk4OTI0OTA0LCJleHAiOjE2OTkwMTEzMDQsInN1YiI6IjYxMTEyOTUiLCJncmFudF90eXBlIjoiIiwiYWNjb3VudF9pZCI6Mjg5MzM5MzYsImJhc2VfZG9tYWluIjoiYW1vY3JtLnJ1IiwidmVyc2lvbiI6Miwic2NvcGVzIjpbInB1c2hfbm90aWZpY2F0aW9ucyIsImZpbGVzIiwiY3JtIiwiZmlsZXNfZGVsZXRlIiwibm90aWZpY2F0aW9ucyJdfQ.lZLsI7x-YNzBEwFT5y_R4bIwO5W2eGmViCPdc3SJufu1xv3MRxYWi_3At833PvhV4bz9dXgTvXxScGASPjVGEHjkiN_Cle6Uy3w0BTh-u3-RhwO_jMuGVgu-bYgug16tuq4U_0KhnKtuF3Ls8yp3MJp2UqLl6TtYNhdytCit3ye3OMVf1hT4N2l577Ddv954QughlCTKUtzn_NiGzL5ipC5fj7jPFQg4V2qPYWgr5zf4dg5n71qBrKR5rKbxoXLog5OJyJmykhEN4at9eo5cyUukMyl-disg91OiS4ygoKcKJEY9hgawyarjHbDDKeOQD6yZXoqb7ilj4UzHbBGF_g'
        self.refresh_token = 'def50200ba360a7a51b3056725bf090576714e4340f68dd13b23dfc8666d62fb8319fc2e09b2cf9cba6d535906d4c2614d8d7eb0b224405ad9e9c457c7ecbdac6fc831cbe046c622452bb9438f7999d67ba6fcba438170fa392814ef91ee010db7fb4aac33b70c29171558609d1191bdc208981cf29adad62a464299d1dbf642493001d50b23d91fb89639ede0497959041c919902186982962d1fd99d893ae69f678c6a54ceceabf88f47929d1146cf1021cb62793b946aa37c4c44fba334ba9eb36f331473208eef125b27caa839c5c908c5a1f6d414f0c8072e60d3a5177f3d3f9cdc43557883c2058650fac608dc837b552a21eb40ff9f991d0f9702108d01a61daf39b064e77421b9c3db4f766ef2986724d2ae2dced801a1f06b2905adc41cb4e060867b17ee8137ae81e25d91c0ddb682d36697e6b1863b94b94ffff495a31ac67fb71b281ebfc14ccf259dc8839970aa19db515c4f34bdd627fa02823f5cecd1d978a4ef7ac24ebc01118faa2ad9cdf73e47c55f65124f8c36ddac681a5d4d654787b93e284b9344ef33b3a415b3aa7f645a59ef17c57fbf2337e2635c5f65fefd0a4cabc7f2312d41a999c6cecde89150858ead4f9e352508ca29e75f9e65a4a4a2da4dea9f4b918d93bf863f1044ff00d3220ae3997b0c8a13fd4802e617c8a63557b8b914c0d7d1'

        self.subdomain = 'https://crmby2021.amocrm.ru/'
        self.api_link = f'{self.subdomain}api/v4/'
        self.headers = {
            "Authorization": "Bearer " + self.access_token
        }

    async def get_access_token_first_time(self) -> None:
        async with aiohttp.ClientSession() as session:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'authorization_code',
                'code': 'def50200d188f82b19049052ed6dac431d6545254d58c3ca1a8ec47f58e443acf3afd4c2e2205dbba74fc58e6215e46fcbb6522ea12cd27495058966ca3124f2edcbeeb1b473e8cc46507fc6b84ee488ead1ec1ff5fdf8da8714e10ecf8b455bb25ac4ce9601564cf8cea51cc8d818a1774d0a94c8ae02cef91f0c30115c6d58bf930a45338427ab268e4f77abfb36255561bec67959a3f62a3da44dc8930bb56e42fa2a3408685a31755c31c1f374bc5483c42beb0caf258e18e70a0969a10bf13f60b1584858724a4b64536b5e869e13c94d7ae40661fe86fc36f02f1a0766683593f5b465129a1f310b4fe6ace4a1bfdccb8ed4bd2f4ed6fa21666ef43640dcaf52caff9ef40bf886dba0138cbdb14c87049a9c6e7e3b46413ec222711021b140e886eb3eef758fa95bc453c9d0acc0bac1bfee80fdbe7fb0ee7bf319383fde19da23e82cbc8a4e377534deb25fc61a27597349c25ae9acf57ea13183625516eaafe592beb1677a4aa36ec30ee5c41063b7368f67b1a16dbd6ec9c56e3e9689d358bbec81818b71e8a7116c594c6279d902143af5d2f53f91cb896c7c3f57be930e09da5d31d29bff075fc497a78c848e68d36af73d8dfa18b1dba0ebed8a5465f0dc2a4c2ff3837e948eaefbb3ef8fc9f34bb0251ccc52b5733e25dc01497b519a495e727a08be',
                'redirect_uri': self.redirect_uri
            }
            async with session.post(url=f'{self.subdomain}oauth2/access_token', data=data) as response:
                result = await response.json()
                print(result)  # записывать в БД result['access_token'], result['refresh_token']
                return

    async def get_new_access_token(self) -> None:
        async with aiohttp.ClientSession() as session:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'redirect_uri': self.redirect_uri
            }
            async with session.post(url='https://crmby2021.amocrm.ru/oauth2/access_token', data=data) as response:
                result = await response.json()
                print(result)  # записывать в БД result['access_token'], result['refresh_token']
                return

    async def __post(self, method: str, data: dict = None) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.api_link}{method}', json=data, headers=self.headers) as response:
                return await response.json()

    async def __get(self, method: str, params: dict = None) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.api_link}{method}', headers=self.headers, params=params) as response:
                return await response.json()

    async def get_custom_fields(self) -> list:
        result = []
        for group in ['leads', 'contacts', 'companies', 'customers']:
            method = f'{group}/custom_fields'
            fields_data = await self.__get(method=method)
            result += fields_data['_embedded']['custom_fields']
            if fields_data['_page_count'] > 1:
                for i in range(2, fields_data['_page_count']+1):
                    fields_data = await self.__get(method=method, params={'page': i})
                    result += fields_data['_embedded']['custom_fields']
        return result


async def main():
    res = await AMO().get_custom_fields()
    pprint(res)


asyncio.run(main())
