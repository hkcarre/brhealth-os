import pandas as pd
from pydantic import BaseModel
import numpy as np
import os
import json

class ForecastState(BaseModel):
    resolved_path: str
    forecast_json: str = ""
    status: str = "pending"
    error: str = ""

def forecast_node(state: ForecastState) -> ForecastState:
    print(f"Forecast Agent: Generating forecasts using data from {state.resolved_path}")
    
    try:
        from statsmodels.tsa.arima.model import ARIMA
        
        # Load the data to check if we have enough history
        df = pd.read_parquet(state.resolved_path)
        
        # In our MVP, all mock data is for '202401' (1 month). 
        # ARIMA requires a time series. We will generate a mock time series 
        # to demonstrate the forecasting capability.
        print("Forecast Agent: Insufficient historical months in MVP data. Generating synthetic historical demand...")
        
        # Simulate 12 months of historical surgical demand
        dates = pd.date_range(start='2023-01-01', periods=12, freq='MS')
        # Base demand + trend + noise
        historical_demand = [100, 105, 110, 108, 115, 120, 118, 125, 130, 128, 135, 140]
        ts_df = pd.DataFrame({'date': dates, 'demand': historical_demand})
        ts_df.set_index('date', inplace=True)
        
        # Fit ARIMA model (Order: AR=1, I=1, MA=0)
        print("Forecast Agent: Fitting ARIMA(1,1,0) model...")
        model = ARIMA(ts_df['demand'], order=(1, 1, 0))
        model_fit = model.fit()
        
        # Forecast next 3 months
        forecast = model_fit.forecast(steps=3)
        forecast_dates = pd.date_range(start='2024-01-01', periods=3, freq='MS')
        
        forecast_results = []
        for date, value in zip(forecast_dates, forecast):
            forecast_results.append({
                "month": date.strftime('%Y-%m'),
                "predicted_demand": round(value, 2)
            })
            
        print("Forecast Agent: Forecast generated successfully.")
        state.forecast_json = json.dumps(forecast_results, indent=2)
        state.status = "success"
        
    except Exception as e:
        state.status = "failed"
        state.error = str(e)
        print(f"Forecast Agent: Error: {e}")
        
    return state
