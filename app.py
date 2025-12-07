from flask import Flask, render_template, jsonify, request
import requests
import datetime
import re

app = Flask(__name__)

# Daily Schedule Definition (Fixed Events + Class Slots)
DAILY_SCHEDULE = [
    {"type": "fixed", "name": "Wake Up", "start": "06:50", "end": "06:50"}, # Instant event representation
    {"type": "fixed", "name": "School Arrival", "start": "06:50", "end": "07:30"},
    {"type": "fixed", "name": "Breakfast", "start": "07:30", "end": "08:10"},
    {"type": "fixed", "name": "Morning Self Study", "start": "08:10", "end": "08:30"},
    {"type": "fixed", "name": "Break", "start": "08:30", "end": "08:40"},
    {"type": "class", "period": 1, "start": "08:40", "end": "09:30"},
    {"type": "break", "name": "Break", "start": "09:30", "end": "09:40"},
    {"type": "class", "period": 2, "start": "09:40", "end": "10:30"},
    {"type": "break", "name": "Break", "start": "10:30", "end": "10:40"},
    {"type": "class", "period": 3, "start": "10:40", "end": "11:30"},
    {"type": "break", "name": "Break", "start": "11:30", "end": "11:40"},
    {"type": "class", "period": 4, "start": "11:40", "end": "12:30"},
    {"type": "fixed", "name": "Lunch Time", "start": "12:30", "end": "13:20", "is_special": True},
    {"type": "class", "period": 5, "start": "13:20", "end": "14:10"},
    {"type": "break", "name": "Break", "start": "14:10", "end": "14:20"},
    {"type": "class", "period": 6, "start": "14:20", "end": "15:10"},
    {"type": "break", "name": "Break", "start": "15:10", "end": "15:20"},
    {"type": "class", "period": 7, "start": "15:20", "end": "16:10"},
    {"type": "fixed", "name": "Cleaning Time", "start": "16:10", "end": "16:30"},
    {"type": "class", "period": 8, "start": "16:30", "end": "17:20", "subject": "After School"},
    {"type": "break", "name": "Break", "start": "17:20", "end": "17:30"}, # Assumed 10m break
    {"type": "class", "period": 9, "start": "17:30", "end": "18:20", "subject": "After School"},
    {"type": "fixed", "name": "Dinner Time", "start": "18:10", "end": "19:00", "is_special": True}, # Overlap adjustment? User said 50m dinner after 8-9. 
    # User said: "8~9교시 후 50분 저녁시간" -> 18:20 end of 9th? 
    # Let's adjust exact request: "8-9교시 (100분)" implies 16:30-18:10? 
    # User Request: "16:30 8교시, 9교시 후 50분 저녁". 
    # Let's stick closer to the user's specific text in request:
    # "8~9교시 (100분)" -> 16:30 ~ 18:10.
    # "50분 저녁" -> 18:10 ~ 19:00.
    # "10~11교시 (100분)" -> 19:00 ~ 20:40.
    
    # Refined Schedule based on prompt text analysis:
    # 7교시 End: 16:10.
    # Cleaning: 20min -> 16:10 - 16:30.
    # 8-9 Period: 100min -> 16:30 - 18:10.
    # Dinner: 50min -> 18:10 - 19:00.
    # 10-11 Period: 100min -> 19:00 - 20:40.
    # Dorm Entry: 20:40.
    # Roll Call: 21:00.
    # Lights Out: 23:00.
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
    
    # Define exact detailed schedule based on user request
    schedule_def = [
        {"time": "06:50 - 07:30", "event": "Wake Up / School Arrival", "type": "life"},
        {"time": "07:30 - 08:10", "event": "Breakfast", "type": "food"},
        {"time": "08:10 - 08:30", "event": "Morning Self Study", "type": "study"},
        {"time": "08:30 - 08:40", "event": "Prophet / Break", "type": "break"}, # User didn't specify what's here, assumes break
        {"time": "08:40 - 09:30", "event": "Period 1", "type": "class", "period": 1},
        {"time": "09:30 - 09:40", "event": "Break", "type": "break"},
        {"time": "09:40 - 10:30", "event": "Period 2", "type": "class", "period": 2},
        {"time": "10:30 - 10:40", "event": "Break", "type": "break"},
        {"time": "10:40 - 11:30", "event": "Period 3", "type": "class", "period": 3},
        {"time": "11:30 - 11:40", "event": "Break", "type": "break"},
        {"time": "11:40 - 12:30", "event": "Period 4", "type": "class", "period": 4},
        {"time": "12:30 - 13:20", "event": "Lunch Time", "type": "food"},
        {"time": "13:20 - 14:10", "event": "Period 5", "type": "class", "period": 5},
        {"time": "14:10 - 14:20", "event": "Break", "type": "break"},
        {"time": "14:20 - 15:10", "event": "Period 6", "type": "class", "period": 6},
        {"time": "15:10 - 15:20", "event": "Break", "type": "break"},
        {"time": "15:20 - 16:10", "event": "Period 7", "type": "class", "period": 7},
        {"time": "16:10 - 16:30", "event": "Cleaning Time", "type": "life"},
        {"time": "16:30 - 18:10", "event": "After School (8-9 Period)", "type": "study"},
        {"time": "18:10 - 19:00", "event": "Dinner Time", "type": "food"},
        {"time": "19:00 - 20:40", "event": "Night Self Study (10-11 Period)", "type": "study"},
        {"time": "20:40 - 21:00", "event": "Dorm Entry", "type": "life"},
        {"time": "21:00 - 23:00", "event": "Roll Call / Rest", "type": "life"},
        {"time": "23:00 - 23:01", "event": "Lights Out", "type": "life"}
    ]

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
