
from typing import List, Dict
import pandas as pd

def compute_moving_averages(df: pd.DataFrame, short: int = 5, long: int = 20) -> pd.DataFrame:
  
    df = df.sort_values("datetime").reset_index(drop=True).copy()
    df["SMA_short"] = df["close"].rolling(window=short, min_periods=1).mean()
    df["SMA_long"] = df["close"].rolling(window=long, min_periods=1).mean()
    df["signal"] = 0
    df.loc[df["SMA_short"] > df["SMA_long"], "signal"] = 1
    df.loc[df["SMA_short"] < df["SMA_long"], "signal"] = -1
    df["signal_change"] = df["signal"].diff().fillna(0)
    return df

def generate_trades(df: pd.DataFrame) -> List[Dict]:
    trades = []
    position = None
    for i in range(len(df)):
        change = df.loc[i, "signal_change"]
        if change > 0 and df.loc[i, "signal"] == 1 and position is None:
            # enter long
            position = {"buy_idx": i, "buy_price": df.loc[i, "close"]}
        elif change < 0 and df.loc[i, "signal"] == -1 and position is not None:
            # exit long
            sell_idx = i
            sell_price = df.loc[i, "close"]
            pnl = sell_price - position["buy_price"]
            trades.append({
                "buy_idx": position["buy_idx"],
                "buy_price": position["buy_price"],
                "sell_idx": sell_idx,
                "sell_price": sell_price,
                "pnl": pnl
            })
            position = None
    if position is not None:
        last_idx = df.index[-1]
        last_price = df.loc[last_idx, "close"]
        pnl = last_price - position["buy_price"]
        trades.append({
            "buy_idx": position["buy_idx"],
            "buy_price": position["buy_price"],
            "sell_idx": last_idx,
            "sell_price": last_price,
            "pnl": pnl
        })
    return trades

def performance_from_trades(trades: List[Dict]) -> Dict:
    total_pnl = sum(t["pnl"] for t in trades)
    wins = sum(1 for t in trades if t["pnl"] > 0)
    losses = sum(1 for t in trades if t["pnl"] <= 0)
    return {
        "total_trades": len(trades),
        "total_pnl": float(total_pnl),
        "winning_trades": wins,
        "losing_trades": losses,
        "avg_pnl_per_trade": float(total_pnl / len(trades)) if trades else 0.0
    }
