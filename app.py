from flask import Flask, render_template, jsonify, request
import requests
import datetime
import re

app = Flask(__name__)

# Constants for Busan Software Meister High School
NEIS_API_KEY = "Type=json&ATPT_OFCDC_SC_CODE=C10&SD_SCHUL_CODE=7150658"
BASE_URL = "https://open.neis.go.kr/hub/"

# Approximate Bell Schedule
BELL_SCHEDULE = {
    1: {"start": "08:30", "end": "09:20"},
    2: {"start": "09:30", "end": "10:20"},
    3: {"start": "10:30", "end": "11:20"},
    4: {"start": "11:30", "end": "12:20"},
    # Lunch 12:20 - 13:20
    5: {"start": "13:20", "end": "14:10"},
    6: {"start": "14:20", "end": "15:10"},
    7: {"start": "15:20", "end": "16:10"},
    8: {"start": "16:30", "end": "17:20"}, # After School 1
    9: {"start": "17:30", "end": "18:20"}, # After School 2
    # Dinner 18:20 - 19:20
    "Dinner": {"start": "18:20", "end": "19:20"},
    10: {"start": "19:20", "end": "20:40"}, # Self Study 1
    11: {"start": "21:00", "end": "22:20"}  # Self Study 2
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/timetable')
def timetable():
    return render_template('timetable.html')

@app.route('/menu')
def menu_page():
    return render_template('menu.html')

# --- Helper Functions ---

def clean_dish_name(dish_name):
    # Remove allergy info (e.g., "Rice(1.2.3)" -> "Rice")
    return re.sub(r'\([0-9\.]+\)', '', dish_name).replace('*', '')

def is_time_in_range(start_str, end_str):
    now = datetime.datetime.now().time()
    try:
        start = datetime.datetime.strptime(start_str, "%H:%M").time()
        end = datetime.datetime.strptime(end_str, "%H:%M").time()
        return start <= now <= end
    except:
        return False

# --- API Endpoints ---

@app.route('/api/timetable')
def get_timetable():
    grade = request.args.get('grade', '1') # Default Grade 1
    class_nm = request.args.get('class', '1') # Default Class 1
    
    today = datetime.datetime.now().strftime('%Y%m%d')
    # Filter by Grade and Class
    url = f"{BASE_URL}hisTimetable?{NEIS_API_KEY}&ALL_TI_YMD={today}&GRADE={grade}&CLASS_NM={class_nm}"
    
    final_timetable = []
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # 1. Standard Classes (1-7)
        if 'hisTimetable' in data:
            rows = data['hisTimetable'][1]['row']
            for row in rows:
                period = int(row['PERIO'])
                sched = BELL_SCHEDULE.get(period, {"start": "-", "end": "-"})
                final_timetable.append({
                    "period": period,
                    "time": f"{sched['start']} - {sched['end']}",
                    "subject": row['ITRT_CNTNT'],
                    "teacher": "-",
                    "is_current": is_time_in_range(sched['start'], sched['end'])
                })
        
        # 2. Inject Periods 8-9 (After School / Self Study)
        for p in [8, 9]:
            sched = BELL_SCHEDULE.get(p)
            final_timetable.append({
                "period": p,
                "time": f"{sched['start']} - {sched['end']}",
                "subject": "After School / Self Study",
                "teacher": "-",
                "is_current": is_time_in_range(sched['start'], sched['end'])
            })
            
        # 3. Inject Dinner
        dinner_sched = BELL_SCHEDULE.get("Dinner")
        final_timetable.append({
            "period": "Dinner",
            "time": f"{dinner_sched['start']} - {dinner_sched['end']}",
            "subject": "Dinner Time",
            "teacher": "-",
            "is_current": is_time_in_range(dinner_sched['start'], dinner_sched['end']),
            "is_special": True # Flag for UI styling
        })
        
        # 4. Inject Periods 10-11 (Night Self Study)
        for p in [10, 11]:
            sched = BELL_SCHEDULE.get(p)
            final_timetable.append({
                "period": p,
                "time": f"{sched['start']} - {sched['end']}",
                "subject": "Night Self Study",
                "teacher": "-",
                "is_current": is_time_in_range(sched['start'], sched['end'])
            })
            
        return jsonify(final_timetable)
        
    except Exception as e:
        print(f"Error fetching timetable: {e}")
        return jsonify([])

@app.route('/api/lunch')
def get_lunch():
    today = datetime.datetime.now().strftime('%Y%m%d')
    # Use mealServiceDietInfo
    url = f"{BASE_URL}mealServiceDietInfo?{NEIS_API_KEY}&MLSV_YMD={today}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if 'mealServiceDietInfo' not in data:
            return jsonify({"date": today, "menu": [], "calories": 0}) 
            
        # Usually lunch is MMEAL_SC_CODE=2. But rows might return Breakfast/Lunch/Dinner.
        # We'll filter for Lunch (2) or just take the first one if unsure. 
        # BSM is a boarding school so might have all 3. We want Lunch.
        
        meal_rows = data['mealServiceDietInfo'][1]['row']
        lunch_row = next((r for r in meal_rows if r['MMEAL_SC_CODE'] == '2'), None)
        
        # If no explicit lunch, fallback to first standard meal
        if not lunch_row and meal_rows:
            lunch_row = meal_rows[0]
            
        if not lunch_row:
             return jsonify({"date": today, "menu": [], "calories": 0})
             
        dish_str = lunch_row['DDISH_NM'] # HTML formatted string with <br/>
        clean_dishes = [clean_dish_name(d.strip()) for d in dish_str.split('<br/>') if d.strip()]
        
        cal_info = lunch_row.get('CAL_INFO', '0 kcal')
        
        # Structure for frontend
        formatted_menu = []
        for dish in clean_dishes:
            formatted_menu.append({
                "category": "Menu", # NEIS doesn't categorize by "Soup/Rice", just a list
                "name": dish
            })
            
        return jsonify({
            "date": today,
            "menu": formatted_menu,
            "calories": cal_info
        })

    except Exception as e:
        print(f"Error fetching lunch: {e}")
        return jsonify({"date": today, "menu": [], "calories": 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
