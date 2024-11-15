from flask import Flask, render_template, request, redirect, url_for
import cv2 #실시간 이미지 처리 기술
import numpy as np  #numpy를 np로 받음
import sqlite3
import base64

app = Flask(__name__)

# 1. 메인 페이지 라우트
@app.route('/')
def index():
    return render_template('index.html')  # 시작 페이지

# 2. 이름 입력 페이지
@app.route('/name', methods=['GET', 'POST'])
def name_input():
    return render_template('name.html')

# 3. 타입별 진단 선택 페이지
@app.route('/type')
def type_selection():
    return render_template('type.html')  # 사용자 이름 전달

#  사진 분석 시작 
@app.route('/chap')
def photo_analysis():  
    return render_template('chapture.html')  # 사진 분석 페이지

# 얼굴 인식 및 피부톤 분석 함수
def analyze_skin_tone(image_data):
    # 데이터 URL에서 Base64 부분만 추출
    header, encoded = image_data.split(',', 1) #base64로 인코딩된 문자열을 가져옴
    image_data = np.frombuffer(base64.b64decode(encoded), np.uint8)   #Base64 인코딩된 문자열을 바이트 데이터로 변환 - np배열로 저장
    img = cv2.imdecode(image_data, cv2.IMREAD_COLOR) #이미지 배열을 실제 이미지로 디코딩, 컬러로 이미지를 읽어들임

    # 얼굴 인식 모델 불러오기
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml') 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 얼굴 탐지
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
    # 얼굴이 감지된 위치와 크기를 담고 있는 리스트 

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
    avg_color_rgb = avg_color[::-1]  #배열형식 반대로
    print(f"얼굴 평균 RGB 색상: {avg_color_rgb}")  # 디버깅용 출력

    # RGB 색상으로 피부톤 분류
    r, g, b = avg_color_rgb

    scores = {'봄웜': 0, '가을웜': 0, '여름쿨': 0, '겨울쿨': 0}

    # 각 퍼스널 컬러의 기준에 따라 점수 부여
    if r > 130 and g > 120 and b > 120:
        scores['봄웜'] += 3
    if r > 120 and g > 120 and b > 110:
        scores['봄웜'] += 1

    if r > 150 and g > 130 and b < 110:
        scores['가을웜'] += 3
    if r > 130 and g < 125 and b < 100:
        scores['가을웜'] += 1

    if r > 120 and g > 110 and b > 110:
        scores['여름쿨'] += 3
    if r > 120 and g > 120 and b > 100:
        scores['여름쿨'] += 1

    if r > 110 and g > 100 and b > 130:
        scores['겨울쿨'] += 3
    if r > 110 and g > 115 and b > 120:
        scores['겨울쿨'] += 1

    # 점수가 가장 높은 톤의 키를 선택
    tone = max(scores, key=scores.get)

    # 데이터베이스에 tone 저장
    conn = sqlite3.connect('tone.db') #tone.db라는 sqlite파일에 연결 - conn은 connection에 약자 
    cursor = conn.cursor()  #커서를 통해 데이터를 삽입,조회,업데이트 할 수 있음
    #execute 테이블 생성 쿼리
    cursor.execute("CREATE TABLE IF NOT EXISTS tones (tone TEXT)") #tones테이블이 없으면 생성하고 tone이라는 컬럼을 추가
    cursor.execute("INSERT INTO tones (tone) VALUES (?)", (tone,)) #tones테이블에 tone을 추가함. ?에 넣을 값 - 튜플(tone,)
    conn.commit() # 값을 업데이트 함
    conn.close()  #db 연결 종료

    return tone

#  설문 시작 라우트
@app.route('/survey')
def survey():
    return render_template('survey.html')  # 설문 페이지

# 설문 점수 수신 라우트
@app.route('/submit_score', methods=['POST'])
def submit_score():  
    data = request.get_json()   #js에서 보낸 score데이터
    score = int(data['score']) #score 키를 이용해 totalscore 값을 가져옴
    
    # 퍼스널 컬러 계산 로직
    if score >= 20:
        tone = '겨울쿨'
    elif score > 15:
        tone = '여름쿨'
    elif score > 10:
        tone = '봄웜'
    else:
        tone = '가을웜'
    
    # 데이터베이스에 톤만 저장
    conn = sqlite3.connect('tone.db')
    cursor = conn.cursor()  
    cursor.execute("CREATE TABLE IF NOT EXISTS tones (tone TEXT)")
    cursor.execute("INSERT INTO tones (tone) VALUES (?)", (tone,))
    conn.commit()
    conn.close()
    
    return tone

#설문,캡처 두 방법이 달라서 톤을 받고 결과페이지에 출력할때 다른 루트를 사용

@app.route('/analyze', methods=['POST'])  
def analyze():
    data = request.get_json()  #json으로 전송된 데이터를 저장
    image_data = data.get('image')   #이미지 데이터 받기 json에서 키값을 사용하여 이미지 데이터 추출
    tone = analyze_skin_tone(image_data)  #함수를 사용해서 이미지 분석
    print(tone)  #터미널에 톤 출력
    return render_template('result.html', tone=tone)  #결과 페이지 랜더링, tone데이터 보내기

# 결과 페이지 
@app.route('/result')
def result():
    # 최근 톤 결과를 가져와 결과 페이지에 전달
    conn = sqlite3.connect('tone.db')
    cursor = conn.cursor() 
    cursor.execute("SELECT tone FROM tones ORDER BY ROWID DESC LIMIT 1")  #가장 최근에 삽입된 하나의 tone 값만 가져옴
    tone = cursor.fetchone()[0]  # 가장 최근 톤 가져오기
    print(tone)  #터미널에 톤 출력
    conn.close()
    
    return render_template('result.html', tone=tone)

if __name__ == '__main__':
    app.run(debug=True)
