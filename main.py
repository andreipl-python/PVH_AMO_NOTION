import asyncio
import models


async def main():
    await models.update_sql_table()
    await models.update_notion_table()


if __name__ == '__main__':
    asyncio.run(main())

