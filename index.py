from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/led/on')
def led_on():
    # GPIO 관련 코드는 제거
    # 예시로 상태만 반환
    return json.dumps({'status': 'ON'})

@app.route('/led/off')
def led_off():
    # GPIO 관련 코드는 제거
    # 예시로 상태만 반환
    return json.dumps({'status': 'OFF'})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
