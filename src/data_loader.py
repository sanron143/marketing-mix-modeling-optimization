import pandas as pd
import numpy as np
import os

def generate_historical_marketing_data():
    np.random.seed(42)
    weeks = 156 # 3 Years of weekly data tracking
    date_range = pd.date_range(start="2023-01-01", periods=weeks, freq="W")
    
    # Generate baseline weekly advertising spends with random variance
    spend_search = np.random.gamma(shape=12, scale=800, size=weeks) + 2000
    spend_social = np.random.gamma(shape=10, scale=1000, size=weeks) + 3000
    spend_banners = np.random.gamma(shape=6, scale=1200, size=weeks) + 1000
    
    df = pd.DataFrame({
        'Week': date_range,
        'Current_Spend_Search': spend_search.round(2),
        'Current_Spend_Social': spend_social.round(2),
        'Current_Spend_Banners': spend_banners.round(2)
    })
    
    # Introduce a base level of sales (organic sales without ads)
    base_sales = 450 + np.random.normal(0, 15, weeks)
    
    # Define simple multipliers to generate historical sales
    df['Conversions'] = (base_sales + 
                         (df['Current_Spend_Search'] * 0.045) + 
                         (df['Current_Spend_Social'] * 0.028) + 
                         (df['Current_Spend_Banners'] * 0.012)).astype(int)
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/marketing_spend_conversions.csv', index=False)
    print("Step 1 Complete: 'data/marketing_spend_conversions.csv' created.")

if __name__ == "__main__":
    generate_historical_marketing_data()