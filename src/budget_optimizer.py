import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.optimize import minimize

def run_mmm_and_optimization():
    # 1. Load data
    df = pd.read_csv('data/marketing_spend_conversions.csv')
    
    # 2. Apply Adstock Transformation (Human Memory Decay)
    def calculate_adstock(spend_series, decay_factor):
        adstocked = np.zeros_like(spend_series)
        for t in range(len(spend_series)):
            if t == 0:
                adstocked[t] = spend_series[t]
            else:
                adstocked[t] = spend_series[t] + decay_factor * adstocked[t-1]
        return adstocked

    df['Adstock_Search'] = calculate_adstock(df['Current_Spend_Search'].values, 0.15)
    df['Adstock_Social'] = calculate_adstock(df['Current_Spend_Social'].values, 0.30)
    df['Adstock_Banners'] = calculate_adstock(df['Current_Spend_Banners'].values, 0.05)
    
    # 3. Train Linear Regression Model 
    X = df[['Adstock_Search', 'Adstock_Social', 'Adstock_Banners']]
    y = df['Conversions']
    
    model = LinearRegression(positive=True) 
    model.fit(X, y)
    
    intercept = model.intercept_
    # extract coefficient vector and individual channel multipliers
    coefs = model.coef_
    coef_search, coef_social, coef_banners = coefs[0], coefs[1], coefs[2]
    
    # 4. Mathematical Optimization Layer
    total_weekly_budget = 25000.00
    
    # objective: compute scalar predicted sales for a given allocation
    def objective(spends):
        predicted_sales = intercept + np.dot(coefs, spends)
        return -float(predicted_sales)

    constraints = ({'type': 'eq', 'fun': lambda spends: np.sum(spends) - total_weekly_budget})
    
    bounds = ((2000, 15000), (2000, 15000), (1000, 10000))
    initial_guess = [total_weekly_budget/3, total_weekly_budget/3, total_weekly_budget/3]
    
    solution = minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    opt_search, opt_social, opt_banners = solution.x
    
    # 5. Export Summary Metrics for Power BI Ingestion
    summary_data = {
        'Metric': ['Google Search Ads', 'Paid Social Media', 'Web Banner Ads', 'Total Suite Context'],
        'Current_Average_Spend': [df['Current_Spend_Search'].mean().round(2), df['Current_Spend_Social'].mean().round(2), df['Current_Spend_Banners'].mean().round(2), total_weekly_budget],
        'Optimized_Recommended_Spend': [round(opt_search, 2), round(opt_social, 2), round(opt_banners, 2), total_weekly_budget],
        'Channel_Power_Multiplier': [round(coef_search, 4), round(coef_social, 4), round(coef_banners, 4), 0.0]
    }
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('data/optimized_allocation_results.csv', index=False)
    print("Step 2 Complete: 'data/optimized_allocation_results.csv' created successfully.")

if __name__ == "__main__":
    run_mmm_and_optimization()