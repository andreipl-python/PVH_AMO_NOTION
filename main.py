import asyncio
import logging

import models


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    logger = logging.getLogger()
    file_handler = logging.FileHandler('logs.log')
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))
    logger.addHandler(file_handler)

    access_token, refresh_token = await models.update_access_data()
    await models.update_sql_table(access_token, refresh_token)
    await models.update_notion_table()


if __name__ == '__main__':
    asyncio.run(main())

