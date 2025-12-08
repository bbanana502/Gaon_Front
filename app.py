from flask import Flask, render_template, jsonify, request
import requests
import datetime
import re

app = Flask(__name__)



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



@app.route('/timetable')
def timetable():
    return render_template('timetable.html')

@app.route('/menu')
def menu_page():
    return render_template('menu.html')

# In-memory storage for user config (Global for demo)
USER_CONFIG = {
    "nickname": "guest1234",
    "gender": None,
    "language": "ko",
    "instructions": None
}

# --- API Endpoints defined in API_SPEC.md ---

@app.route('/school/meal', methods=['GET'])
def school_meal():
    date_str = request.args.get('day', datetime.datetime.now().strftime('%Y-%m-%d'))
    return jsonify({
        "date": date_str,
        "schoolName": "부산소프트웨어마이스터고등학교",
        "items": [
            {"dish": "쌀밥/잡곡밥, 쇠고기미역국, 닭볶음탕, 배추김치", "calories": "750 Kcal", "nutrients": "단백질 30g, 탄수화물 100g", "type": "breakfast"},
            {"dish": "제육덮밥, 콩나물국, 깍두기, 요플레", "calories": "850 Kcal", "nutrients": "단백질 35g, 탄수화물 110g", "type": "lunch"},
            {"dish": "카레라이스, 장국, 단무지, 핫도그", "calories": "800 Kcal", "nutrients": "단백질 25g, 탄수화물 120g", "type": "dinner"}
        ]
    })

@app.route('/school/event', methods=['GET'])
def school_event():
    month_str = request.args.get('month', datetime.datetime.now().strftime('%Y-%m'))
    return jsonify({
        "month": month_str,
        "schoolName": "부산소프트웨어마이스터고등학교",
        "items": [
            {
                "title": "개학식",
                "startDate": f"{month_str}-02",
                "endDate": f"{month_str}-02",
                "description": "2학기 개학식입니다."
            }
        ]
    })

@app.route('/school/timetable', methods=['GET'])
def school_timetable():
    date_str = request.args.get('day', datetime.datetime.now().strftime('%Y-%m-%d'))
    # Mock data for 7 periods
    items = []
    subjects = ["국어", "수학", "영어", "과학", "사회", "체육", "음악"]
    for i in range(1, 8):
        items.append({
            "period": str(i),
            "subject": subjects[i-1],
            "teacher": f"선생님{i}",
            "classroom": f"1-{i}"
        })
        
    return jsonify({
        "date": date_str,
        "schoolName": "부산소프트웨어마이스터고등학교",
        "items": items
    })

@app.route('/music', methods=['GET'])
def music():
    title = request.args.get('title')
    # Dummy implementation - file not found
    return jsonify({"detail": f"music '{title}' not found"}), 404

@app.route('/speaker/connect', methods=['POST'])
def speaker_connect():
    return jsonify({
        "status": "ok",
        "protocol": "mcp",
        "version": "1.0",
        "deviceId": request.headers.get('X-Device-Id')
    })

@app.route('/user/config', methods=['GET', 'PUT'])
def user_config():
    global USER_CONFIG
    if request.method == 'PUT':
        data = request.json
        USER_CONFIG.update(data)
        return jsonify(USER_CONFIG)
    return jsonify(USER_CONFIG)

@app.route('/user/me', methods=['GET'])
def user_me():
    return jsonify(USER_CONFIG)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
