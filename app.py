from flask import Flask, render_template, jsonify, request
import requests
import datetime
import re

app = Flask(__name__)

# Constants for Busan Software Meister High School
NEIS_API_KEY = "Type=json&ATPT_OFCDC_SC_CODE=C10&SD_SCHUL_CODE=7150658"
BASE_URL = "https://open.neis.go.kr/hub/"

# Daily Schedule Definition (Fixed Events + Class Slots)
DAILY_SCHEDULE = [
    {"type": "fixed", "name": "기상", "start": "06:50", "end": "06:50"}, # Instant event representation
    {"type": "fixed", "name": "등교", "start": "06:50", "end": "07:30"},
    {"type": "fixed", "name": "아침 식사", "start": "07:30", "end": "08:10"},
    {"type": "fixed", "name": "아침 자습", "start": "08:10", "end": "08:30"},
    {"type": "fixed", "name": "쉬는 시간", "start": "08:30", "end": "08:40"},
    {"type": "class", "period": 1, "start": "08:40", "end": "09:30"},
    {"type": "break", "name": "쉬는 시간", "start": "09:30", "end": "09:40"},
    {"type": "class", "period": 2, "start": "09:40", "end": "10:30"},
    {"type": "break", "name": "쉬는 시간", "start": "10:30", "end": "10:40"},
    {"type": "class", "period": 3, "start": "10:40", "end": "11:30"},
    {"type": "break", "name": "쉬는 시간", "start": "11:30", "end": "11:40"},
    {"type": "class", "period": 4, "start": "11:40", "end": "12:30"},
    {"type": "fixed", "name": "점심 시간", "start": "12:30", "end": "13:20", "is_special": True},
    {"type": "class", "period": 5, "start": "13:20", "end": "14:10"},
    {"type": "break", "name": "쉬는 시간", "start": "14:10", "end": "14:20"},
    {"type": "class", "period": 6, "start": "14:20", "end": "15:10"},
    {"type": "break", "name": "쉬는 시간", "start": "15:10", "end": "15:20"},
    {"type": "class", "period": 7, "start": "15:20", "end": "16:10"},
    {"type": "fixed", "name": "청소 시간", "start": "16:10", "end": "16:30"},
    {"type": "class", "period": 8, "start": "16:30", "end": "17:20", "subject": "방과후 수업"},
    {"type": "break", "name": "쉬는 시간", "start": "17:20", "end": "17:30"}, 
    {"type": "class", "period": 9, "start": "17:30", "end": "18:20", "subject": "방과후 수업"},
    {"type": "fixed", "name": "저녁 식사", "start": "18:10", "end": "19:00", "is_special": True}, 
    {"type": "fixed", "name": "야간 자율 학습 (10-11교시)", "start": "19:00", "end": "20:40"},
    {"type": "fixed", "name": "기숙사 입실", "start": "20:40", "end": "21:00"},
    {"type": "fixed", "name": "점호 / 휴식", "start": "21:00", "end": "23:00"},
    {"type": "fixed", "name": "소등", "start": "23:00", "end": "23:01"}
]

# Re-defining constants for internal use if needed, but mainly loop-driven now.

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
    # Filter by Grade and Class for NEIS
    url = f"{BASE_URL}hisTimetable?{NEIS_API_KEY}&ALL_TI_YMD={today}&GRADE={grade}&CLASS_NM={class_nm}"
    
    try:
        neis_data = {}
        response = requests.get(url)
        json_resp = response.json()
        
        if 'hisTimetable' in json_resp:
            rows = json_resp['hisTimetable'][1]['row']
            for row in rows:
                neis_data[int(row['PERIO'])] = row['ITRT_CNTNT']
    except Exception:
        neis_data = {}

    final_timetable = []
    
    # Use global translated schedule
    schedule_def = DAILY_SCHEDULE

    for item in schedule_def:
        subject = item['event']
        teacher = "-"
        
        # Override Subject if it's a class and we have NEIS data
        if item.get('type') == 'class':
            period_num = item.get('period')
            if period_num in neis_data:
                subject = neis_data[period_num]
        
        times = item['time'].split(' - ')
        start, end = times[0], times[1]
        
        final_timetable.append({
            "period": item.get('period', '-') if item.get('type') == 'class' else "", 
            "time": item['time'],
            "subject": subject,
            "teacher": teacher,
            "is_current": is_time_in_range(start, end),
            "is_special": item.get('type') in ['food', 'life'], # Style these differently
            "type": item.get('type') # Pass type for frontend custom styling if needed
        })
            
    return jsonify(final_timetable)

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
