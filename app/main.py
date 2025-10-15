# app/main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.database import db, connect_db, disconnect_db
from app.schemas import StockDataSchema
from app.strategy import compute_moving_averages, generate_trades, performance_from_trades
import pandas as pd

app = FastAPI(title="Invsto Assignment")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

@app.get("/data")
async def get_data(limit: int = Query(default=1000, ge=1)):
    rows = await db.stockdata.find_many()
    return rows

@app.post("/data")
async def add_data(record: StockDataSchema):
    try:
        created = await db.stockdata.create(data=record.model_dump())
        return {"message": "Record added successfully", "data": created}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/strategy/performance")
async def strategy_performance(short: int = 5, long: int = 20):
    if short >= long:
        raise HTTPException(status_code=400, detail="short must be less than long")
    rows = await db.stockdata.find_many()
    if not rows:
        return {"error": "no data in database"}
    df = pd.DataFrame([
        {
            "datetime": r.datetime.isoformat() if hasattr(r.datetime, "isoformat") else r.datetime,
            "close": float(r.close)
        }
        for r in rows
    ])


    # ensure datetime typed
    df["datetime"] = pd.to_datetime(df["datetime"])
    if df.empty or df.shape[0] < long:
        return {"error": f"not enough data to compute long moving average (need at least {long} rows)"}
    processed = compute_moving_averages(df, short=short, long=long)
    trades = generate_trades(processed)
    perf = performance_from_trades(trades)
    return {"performance": perf, "trades": trades}
