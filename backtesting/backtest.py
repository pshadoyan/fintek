from fastapi import FastAPI, HTTPException
from backtesting import Backtest, Strategy
from backtesting.test import GOOG
import pandas as pd
import numpy as np
import itertools
import logging
from typing import Dict, List

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PandasMeanReversionStrategy(Strategy):
    # Define strategy parameters
    bb_period = 20
    rsi_period = 14
    atr_period = 14
    atr_multiplier = 2

    def init(self):
        close = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)

        sma = close.rolling(self.bb_period).mean()
        std = close.rolling(self.bb_period).std()
        self.bb_upper = sma + 2 * std
        self.bb_lower = sma - 2 * std

        delta = close.diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ma_up = up.rolling(self.rsi_period).mean()
        ma_down = down.rolling(self.rsi_period).mean()
        self.rsi = 100 - (100 / (1 + ma_up / ma_down))

        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        self.atr = true_range.rolling(self.atr_period).mean()

        self.trail_high = 0
        self.trail_low = np.inf

    def next(self):
        last_index = len(self.data.Close) - 1

        if not self.position:
            if self.data.Close[last_index] < self.bb_lower.iloc[last_index] and self.rsi.iloc[last_index] < 30:
                self.buy()
            elif self.data.Close[last_index] > self.bb_upper.iloc[last_index] and self.rsi.iloc[last_index] > 70:
                self.sell()
        else:
            if self.position.is_long:
                self.trail_high = max(self.trail_high, self.data.High[last_index])
                if self.data.Close[last_index] <= self.trail_high - self.atr.iloc[last_index] * self.atr_multiplier:
                    self.position.close()
                    self.trail_high = 0
            elif self.position.is_short:
                self.trail_low = min(self.trail_low, self.data.Low[last_index])
                if self.data.Close[last_index] >= self.trail_low + self.atr.iloc[last_index] * self.atr_multiplier:
                    self.position.close()
                    self.trail_low = np.inf

class Strategy1(Strategy):
    # Strategy1 implementation
    ...

# More strategy classes can be added similarly

# Strategy mapping for easy selection
strategies = {
    "PandasMeanReversionStrategy": PandasMeanReversionStrategy,
    "Strategy1": Strategy1,
    # Add other strategies to this mapping
}

# Function to run the backtest
def run_backtest(strategy_name: str) -> List[Dict]:
    if strategy_name not in strategies:
        raise ValueError(f"Strategy '{strategy_name}' not found")

    StrategyClass = strategies[strategy_name]

    # Parameter ranges for hyperparameter optimization
    # This can be customized per strategy if needed
    bb_period_range = range(15, 26, 5)  # Example: 15, 20, 25
    rsi_period_range = range(10, 21, 5) # Example: 10, 15, 20
    atr_period_range = range(10, 21, 5) # Example: 10, 15, 20
    atr_multiplier_range = [1, 1.5, 2, 2.5, 3]

    results = []

    for bb_period, rsi_period, atr_period, atr_multiplier in itertools.product(
            bb_period_range, rsi_period_range, atr_period_range, atr_multiplier_range):

        # Set the strategy parameters dynamically
        StrategyClass.bb_period = bb_period
        StrategyClass.rsi_period = rsi_period
        StrategyClass.atr_period = atr_period
        StrategyClass.atr_multiplier = atr_multiplier

        bt = Backtest(GOOG, StrategyClass, cash=10000, commission=.002)
        stats = bt.run()

        results.append({
            "strategy": strategy_name,
            "params": {
                "bb_period": bb_period,
                "rsi_period": rsi_period,
                "atr_period": atr_period,
                "atr_multiplier": atr_multiplier
            },
            "return": stats['Return [%]']
        })

    # Sort results by return and return top 10
    top_results = sorted(results, key=lambda x: x['return'], reverse=True)[:10]
    
    return bt, top_results

# FastAPI app
app = FastAPI()

@app.get("/run-backtest/")
async def run_backtest_endpoint(strategy: str):
    try:
        x, results = run_backtest(strategy)
        return results
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Additional code for running the server, if needed
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)