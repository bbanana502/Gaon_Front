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
        subject = item.get('name', '')
        teacher = "-"
        
        # Override Subject if it's a class and we have NEIS data
        if item.get('type') == 'class':
            period_num = item.get('period')
            # Override name with "Period X" placeholder if no specific name provided in struct, 
            # though global struct has no "name" for classes usually, let's allow fallback.
            if period_num in neis_data:
                subject = neis_data[period_num]
            elif not subject: # If subject is empty strings (for classes in global dict?)
                 subject = f"{period_num}교시"
        
        # Construct time string from start/end
        start = item['start']
        end = item['end']
        time_str = f"{start} - {end}"
        
        final_timetable.append({
            "period": item.get('period', '-') if item.get('type') == 'class' else "", 
            "time": time_str,
            "subject": subject,
            "teacher": teacher,
            "is_current": is_time_in_range(start, end),
            "is_special": item.get('type') in ['food', 'life'], 
            "type": item.get('type') 
        })
            
    return jsonify(final_timetable)

# Standard NEIS Allergy Codes
ALLERGY_MAP = {
    "1": "난류", "2": "우유", "3": "메밀", "4": "땅콩", "5": "대두",
    "6": "밀", "7": "고등어", "8": "게", "9": "새우", "10": "돼지고기",
    "11": "복숭아", "12": "토마토", "13": "아황산류", "14": "호두", "15": "닭고기",
    "16": "쇠고기", "17": "오징어", "18": "조개류", "19": "잣"
}

def parse_dish(dish_string):
    """
    Parses a dish string like "Rice(1.2)" into name and list of allergies.
    """
    # Extract allergy numbers: (1.2.3)
    match = re.search(r'\(([\d\.]+)\)', dish_string)
    allergies = []
    clean_name = dish_string
    
    if match:
        codes = match.group(1).split('.')
        for code in codes:
            if code in ALLERGY_MAP:
                allergies.append(ALLERGY_MAP[code])
        # Remove the code part from name for display
        clean_name = re.sub(r'\([0-9\.]+\)', '', dish_string).replace('*', '')
        
    return {
        "name": clean_name.strip(),
        "allergies": allergies
    }

@app.route('/api/meals')
def get_meals():
    today = datetime.datetime.now().strftime('%Y%m%d')
    url = f"{BASE_URL}mealServiceDietInfo?{NEIS_API_KEY}&MLSV_YMD={today}"
    
    meals = {
        "breakfast": {"menu": [], "calories": "0 Kcal"},
        "lunch": {"menu": [], "calories": "0 Kcal"},
        "dinner": {"menu": [], "calories": "0 Kcal"}
    }
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if 'mealServiceDietInfo' in data:
            rows = data['mealServiceDietInfo'][1]['row']
            
            for row in rows:
                # MMEAL_SC_CODE: 1=Breakfast, 2=Lunch, 3=Dinner
                code = row['MMEAL_SC_CODE']
                meal_type = ""
                if code == "1": meal_type = "breakfast"
                elif code == "2": meal_type = "lunch"
                elif code == "3": meal_type = "dinner"
                
                if meal_type:
                    dish_str = row['DDISH_NM']
                    # Split by <br/> -> parse each dish
                    parsed_menu = [parse_dish(d.strip()) for d in dish_str.split('<br/>') if d.strip()]
                    meals[meal_type]["menu"] = parsed_menu
                    meals[meal_type]["calories"] = row.get('CAL_INFO', '0 Kcal')

        return jsonify({
            "date": today,
            "meals": meals
        })

    except Exception as e:
        print(f"Error fetching meals: {e}")
        return jsonify({"date": today, "meals": meals})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
