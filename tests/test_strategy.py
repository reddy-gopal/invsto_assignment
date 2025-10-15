import unittest
import pandas as pd
from app.strategy import compute_moving_averages, generate_trades, performance_from_trades

class TestStrategy(unittest.TestCase):
    def setUp(self):
        data = {
            "datetime": pd.date_range(start="2025-01-01", periods=10, freq="D"),
            "close": [10,11,12,13,14,15,14,13,12,11]
        }
        self.df = pd.DataFrame(data)

    def test_moving_average_columns(self):
        processed = compute_moving_averages(self.df.copy(), short=2, long=3)
        self.assertIn("SMA_short", processed.columns)
        self.assertIn("SMA_long", processed.columns)
        self.assertIn("signal", processed.columns)

    def test_generate_trades_and_performance(self):
        processed = compute_moving_averages(self.df.copy(), short=2, long=3)
        trades = generate_trades(processed)
        perf = performance_from_trades(trades)
        self.assertIsInstance(trades, list)
        self.assertIn("total_trades", perf)
        self.assertGreaterEqual(perf["total_trades"], 0)

if __name__ == "__main__":
    unittest.main()
