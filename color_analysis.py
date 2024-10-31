from flask import Flask, request, render_template
import cv2
import numpy as np
import sqlite3
import base64  # base64 모듈을 추가합니다.

app = Flask(__name__)

# 피부톤 분석 함수
def analyze_skin_tone(image_data):
    # 데이터 URL에서 Base64 부분만 추출
    header, encoded = image_data.split(',', 1)
    image_data = np.frombuffer(base64.b64decode(encoded), np.uint8)
    img = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    # 이미지에서 평균 색상 계산
    avg_color_per_row = np.average(img, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)

    # BGR에서 RGB로 변환
    avg_color_rgb = avg_color[::-1]

    # RGB 색상으로 피부톤 분류
    r, g, b = avg_color_rgb
    if r > 130 and g > 90 and b < 80:
        tone = '봄웜'
    elif r > 90 and g < 70 and b < 60:
        tone = '가을웜'
    elif r < 100 and g < 110 and b > 140:
        tone = '여름쿨'
    else:
        tone = '겨울쿨'

    # 데이터베이스에 저장
    conn = sqlite3.connect('tone.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS tones (tone TEXT)")
    cursor.execute("INSERT INTO tones (tone) VALUES (?)", (tone,))
    conn.commit()
    conn.close()

    return tone

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    image_data = data.get('image')
    tone = analyze_skin_tone(image_data)
    return render_template('result1.html', tone=tone)

@app.route('/')
def index():
    return render_template('chapture.html')

if __name__ == '__main__':
    app.run(debug=True)
