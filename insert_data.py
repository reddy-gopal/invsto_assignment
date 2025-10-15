import pandas as pd
import asyncio
from prisma import Prisma

db = Prisma()


async def main():
    await db.connect()
    df = pd.read_csv('data.csv')

    for _, row in df.iterrows():
        await db.stockdata.create(
            data={
                "datetime": pd.to_datetime(row['datetime']),
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": int(row['volume']),
            }
        )

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
