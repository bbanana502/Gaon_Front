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

from functools import lru_cache
import time

# --- Helper Functions ---

def clean_dish_name(dish_name):
    # Remove allergy info (e.g., "Rice(1.2.3)" -> "Rice")
    return re.sub(r'\([0-9\.]+\)', '', dish_name).replace('*', '')

def is_time_in_range(start_str, end_str, target_date_str=None):
    """
    Checks if current time is within range.
    If target_date_str is provided, it must match today's date for this to potentially be true.
    """
    now_dt = datetime.datetime.now()
    today_str = now_dt.strftime('%Y%m%d')
    
    # If looking at a different date, nothing is "current"
    if target_date_str and target_date_str != today_str:
        return False

    now = now_dt.time()
    try:
        start = datetime.datetime.strptime(start_str, "%H:%M").time()
        end = datetime.datetime.strptime(end_str, "%H:%M").time()
        return start <= now <= end
    except:
        return False

# --- Cached Data Fetchers ---
# Cache up to 128 different combinations (Date+Grade+Class)
# Since NEIS data doesn't change minutely, this is safe. 
# Restarting app clears cache.

@lru_cache(maxsize=128)
def fetch_neis_timetable_cached(date_str, grade, class_nm):
    url = f"{BASE_URL}hisTimetable?{NEIS_API_KEY}&ALL_TI_YMD={date_str}&GRADE={grade}&CLASS_NM={class_nm}"
    # Let exceptions propagate so they aren't cached
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    json_resp = response.json()
    
    neis_data = {}
    if 'hisTimetable' in json_resp:
        rows = json_resp['hisTimetable'][1]['row']
        for row in rows:
            neis_data[int(row['PERIO'])] = row['ITRT_CNTNT']
    return neis_data

# --- API Endpoints ---

@app.route('/api/timetable')
def get_timetable():
    grade = request.args.get('grade', '1') # Default Grade 1
    class_nm = request.args.get('class', '1') # Default Class 1
    date_str = request.args.get('date', datetime.datetime.now().strftime('%Y%m%d')) # Default Today
    
    # Use cached function, handle failures gracefully
    try:
        neis_data = fetch_neis_timetable_cached(date_str, grade, class_nm)
    except Exception as e:
        print(f"Timetable API Error (Not Cached): {e}")
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
            if period_num in neis_data:
                subject = neis_data[period_num]
            elif not subject: 
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
            "is_current": is_time_in_range(start, end, date_str),
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
    match = re.search(r'\(([\d\.]+)\)', dish_string)
    allergies = []
    clean_name = dish_string
    
    if match:
        codes = match.group(1).split('.')
        for code in codes:
            if code in ALLERGY_MAP:
                allergies.append(ALLERGY_MAP[code])
        clean_name = re.sub(r'\([0-9\.]+\)', '', dish_string).replace('*', '')
        
    return {
        "name": clean_name.strip(),
        "allergies": allergies
    }

@lru_cache(maxsize=128)
def fetch_neis_meals_cached(date_str):
    url = f"{BASE_URL}mealServiceDietInfo?{NEIS_API_KEY}&MLSV_YMD={date_str}"
    # Propagate exceptions to avoid caching failures
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    meals = {
        "breakfast": {"menu": [], "calories": "0 Kcal"},
        "lunch": {"menu": [], "calories": "0 Kcal"},
        "dinner": {"menu": [], "calories": "0 Kcal"}
    }
                    
    # Wait, `parse_dish` is defined around line 170. This block replaces line 199. 
    # So `fetch_neis_meals_cached` will be above `parse_dish`. This will error if I call `parse_dish` inside it immediately if not careful.
    # But I'm defining the function. The content isn't executed until `get_meals` calls it.
    # By the time `get_meals` calls it, `parse_dish` (global) will be defined. So it is SAFE.
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'mealServiceDietInfo' in data:
            rows = data['mealServiceDietInfo'][1]['row']
            
            for row in rows:
                code = row['MMEAL_SC_CODE']
                meal_type = ""
                if code == "1": meal_type = "breakfast"
                elif code == "2": meal_type = "lunch"
                elif code == "3": meal_type = "dinner"
                
                if meal_type:
                    dish_str = row['DDISH_NM']
                    parsed_menu = [parse_dish(d.strip()) for d in dish_str.split('<br/>') if d.strip()]
                    meals[meal_type]["menu"] = parsed_menu
                    meals[meal_type]["calories"] = row.get('CAL_INFO', '0 Kcal')
    except Exception as e:
        print(f"Error fetching meals: {e}")
        
    return meals

@app.route('/api/meals')
def get_meals():
    date_str = request.args.get('date', datetime.datetime.now().strftime('%Y%m%d')) # Default Today
    
    # Use cached function
    meals = fetch_neis_meals_cached(date_str)

    return jsonify({
        "date": date_str,
        "meals": meals
    })

import os
import google.generativeai as genai

# ... (Previous code)

# Configure Gemini
# Configure Gemini
# NOTE: API Key provided by user
GEMINI_API_KEY = "AIzaSyA29PHUX7dlyev9Q5OXCWlracAMfJ23ksc"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    user_message = request.json.get('message', '')
    
    if not GEMINI_API_KEY:
        return jsonify({"response": "죄송합니다. 서버에 Gemini API Key가 설정되지 않아 AI와 대화할 수 없습니다."})

    try:
        # 1. Fetch Context Data (Today)
        today_str = datetime.datetime.now().strftime('%Y%m%d')
        
        # We can reuse our existing functions if we refactor them to return data dictionaries 
        # instead of JSON responses, but for simplicity/speed let's make internal helper calls or just quick fetch.
        # Actually, get_meals returns a Response object (jsonify). 
        # We should probably do a quick internal fetch logic since we are within the same app.
        
        # --- Internal Fetch Logic for Context ---
        
        # Meal Context
        meal_url = f"{BASE_URL}mealServiceDietInfo?{NEIS_API_KEY}&MLSV_YMD={today_str}"
        meal_context = "오늘의 급식 정보가 없습니다."
        try:
            m_resp = requests.get(meal_url).json()
            if 'mealServiceDietInfo' in m_resp:
                rows = m_resp['mealServiceDietInfo'][1]['row']
                meal_context = "오늘의 급식:\n"
                for row in rows:
                    meal_name = row['MMEAL_SC_NM'] # e.g. 조식
                    dish_nm = row['DDISH_NM'].replace('<br/>', ', ')
                    dish_clean = re.sub(r'\([0-9\.]+\)', '', dish_nm) # Remove allergy codes for AI context to save tokens/cleanliness
                    meal_context += f"- {meal_name}: {dish_clean}\n"
        except:
            pass

        # Timetable Context (Default Grade 1 Class 1 for generic context, or we could ask user)
        # For now, let's provide a generic 1-1 timetable or just say "I can look up timetables if you tell me your grade/class".
        # Let's just provide the "Daily Schedule" structure (Periods) which is fixed.
        schedule_context = "오늘의 일과표:\n"
        for item in DAILY_SCHEDULE:
            schedule_context += f"- {item['start']}~{item['end']}: {item['name'] if 'name' in item else str(item.get('period'))+'교시'}\n"

        # 2. System Prompt
        system_prompt = f"""
        당신은 부산소프트웨어마이스터고의 AI 비서 '가온(Gaon)'입니다.
        학생들의 학교 생활을 돕기 위해 존재합니다. 친절하고 명랑한 말투를 사용하세요.
        이모지를 적절히 사용하여 생동감 있게 대답해 주세요.

        [오늘의 정보]
        날짜: {today_str}
        {meal_context}
        
        [기본 일과 시간표]
        {schedule_context}
        
        학생의 질문에 위 정보를 바탕으로 답변해 주세요. 정보가 없으면 모른다고 솔직하게 말하세요.
        """
        
        # 3. Call Gemini
        # Using 'gemini-flash-latest' as it was confirmed available in the user's account
        model = genai.GenerativeModel('gemini-flash-latest')
        chat = model.start_chat(history=[])
        response = chat.send_message(system_prompt + "\n\n학생 질문: " + user_message)
        
        return jsonify({"response": response.text})

    except Exception as e:
        print(f"AI Error: {e}")
        return jsonify({"response": "죄송합니다. AI 서비스에 일시적인 문제가 발생했습니다."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
