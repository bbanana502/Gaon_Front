
import sys
import os
import datetime

# Add current directory to path
sys.path.append(os.getcwd())

from app import fetch_neis_meals_cached

today_str = datetime.datetime.now().strftime('%Y%m%d')
print(f"Testing Meal Fetch for Today ({today_str})...")

try:
    start_time = datetime.datetime.now()
    meals = fetch_neis_meals_cached(today_str)
    end_time = datetime.datetime.now()
    
    duration = (end_time - start_time).total_seconds()
    print(f"Fetch completed in {duration:.2f} seconds.")
    
    if meals:
        b_len = len(meals.get('breakfast', {}).get('menu', []))
        l_len = len(meals.get('lunch', {}).get('menu', []))
        d_len = len(meals.get('dinner', {}).get('menu', []))
        print(f"Result: Breakfast({b_len}), Lunch({l_len}), Dinner({d_len})")
    else:
        print("Result: Empty meals dictionary returned.")
        
except Exception as e:
    print(f"Fetch Failed with Exception: {e}")
