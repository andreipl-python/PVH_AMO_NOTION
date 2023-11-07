import asyncio
import logging

import models


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    access_token, refresh_token = await models.update_access_data()
    await models.update_sql_table(access_token, refresh_token)
    await models.update_notion_table()


if __name__ == '__main__':
    asyncio.run(main())

