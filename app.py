from flask import Flask, render_template, request, redirect, url_for
import cv2
import numpy as np
import sqlite3
import base64

app = Flask(__name__)

# 1. 메인 페이지 라우트
@app.route('/')
def index():
    return render_template('index.html')  # 시작 페이지

# 2. 이름 입력 페이지 라우트
@app.route('/name', methods=['GET', 'POST'])
def name_input():
    return render_template('name.html')

# 3. 타입별 진단 선택 페이지 라우트
@app.route('/type')
def type_selection():
    return render_template('type.html')  # 사용자 이름 전달

# 4. 설문 시작 라우트
@app.route('/survey')
def survey():
    return render_template('survey.html')  # 설문 페이지

# 5. 사진 분석 시작 라우트
@app.route('/chap')
def photo_analysis():
    return render_template('chapture.html')  # 사진 분석 페이지

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

  # 퍼스널 컬러 분류 기준 조정
    if r > 150 and g > 130 and b > 120:
        tone = '봄웜'  # 밝고 따뜻한 피부 톤
    elif 150 > r and 130 > r and b > 100:
        tone = '가을웜'  # 다소 깊은 따뜻한 톤
    elif r > 130 and g > 130 and b > 140:
        tone = '여름쿨'  # 밝고 차가운 톤
    elif r > 160 and g > 150 and b > 150:
        tone = '겨울쿨'  # 차갑고 선명한 톤
    else:
        tone = '측정할 수 없음'

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
    return render_template('result1.html', tone=tone)


# 6. 결과 페이지 라우트 (설문 또는 사진 결과)
@app.route('/result')
def result():
    return render_template('result.html')  # 결과 페이지

if __name__ == '__main__':
    app.run(debug=True)