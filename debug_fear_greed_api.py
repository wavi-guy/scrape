import asyncio
import aiohttp

async def main():
    url = 'https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical'
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '0ec32b61-d462-4be5-92f5-85d4f14ec474'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            print('Status:', resp.status)
            print('Headers:', dict(resp.headers))
            print('Text:', await resp.text())

if __name__ == '__main__':
    asyncio.run(main())
