from flask import Flask, request, render_template
import cv2
import numpy as np
import sqlite3
import base64

app = Flask(__name__)

# 얼굴 인식 및 피부톤 분석 함수
def analyze_skin_tone(image_data):
    # 데이터 URL에서 Base64 부분만 추출
    header, encoded = image_data.split(',', 1)
    image_data = np.frombuffer(base64.b64decode(encoded), np.uint8)
    img = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    # 얼굴 인식 모델 불러오기
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 얼굴 탐지
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

    # 얼굴이 감지되지 않으면 종료
    if len(faces) == 0:
        return "얼굴이 인식되지 않았습니다."

    # 첫 번째 얼굴 영역 선택
    (x, y, w, h) = faces[0]
    face_region = img[y:y+h, x:x+w]

    # 얼굴 영역에서 평균 색상 계산
    avg_color_per_row = np.average(face_region, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)

    # BGR에서 RGB로 변환
    avg_color_rgb = avg_color[::-1]
    print(f"얼굴 평균 RGB 색상: {avg_color_rgb}")  # 디버깅용 출력

    # RGB 색상으로 피부톤 분류
    r, g, b = avg_color_rgb

    scores = {'봄웜': 0, '가을웜': 0, '여름쿨': 0, '겨울쿨': 0}

    # 조건을 완화하고 각 퍼스널 컬러의 기준에 따라 점수 부여
    if r > 140 and g > 130 and b > 120:
        scores['봄웜'] += 3
    if r > 120 and g > 100 and b > 100:
        scores['봄웜'] += 1

    if r < 150 and g < 130 and b < 110:
        scores['가을웜'] += 3
    if r < 140 and g < 125 and b < 100:
        scores['가을웜'] += 1

    if r > 130 and g > 130 and b > 140:
        scores['여름쿨'] += 3
    if r > 120 and g > 120 and b > 130:
        scores['여름쿨'] += 1

    if r > 160 and g > 150 and b > 150:
        scores['겨울쿨'] += 3
    if r > 150 and g > 140 and b > 140:
        scores['겨울쿨'] += 1

    # 점수가 가장 높은 톤을 선택
    tone = max(scores, key=scores.get)

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
    print(tone)
    return render_template('result.html', tone=tone)

@app.route('/')
def index():
    return render_template('chapture.html')

if __name__ == '__main__':
    app.run(debug=True)
