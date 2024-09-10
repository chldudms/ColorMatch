from flask import Flask, render_template, request
import cv2
import numpy as np
import base64
import random

app = Flask(__name__)

# 얼굴 인식 모델 로드
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def analyze_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 얼굴 검출
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        print("No faces detected")
        return "unknown"  # 얼굴이 검출되지 않으면 처리

    # 첫 번째 얼굴만 사용
    (x, y, w, h) = faces[0]
    
    # 얼굴 영역에서 피부 색상의 평균 밝기 계산
    face_img = gray[y:y+h, x:x+w]
    avg_brightness = np.mean(face_img)
    
    print(f"Average brightness: {avg_brightness}")

    # 단순화된 톤 분석: 밝기가 낮으면 웜톤, 높으면 쿨톤으로 판단
    if avg_brightness < 100:  # 임계값은 조정 가능
        return "warm"
    else:
        return "cool"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    image_data = request.form['image_data']
    # Base64로 인코딩된 이미지를 디코딩
    encoded_image = image_data.split(',')[1]
    decoded_image = base64.b64decode(encoded_image)
    np_image = np.frombuffer(decoded_image, np.uint8)
    image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

    # 얼굴 인식 및 피부 톤 분석
    result = analyze_image(image)

    # 분석 결과에 따른 페이지 렌더링
    if result == "warm":
        return render_template('warm.html', image_data=image_data)
    elif result == "cool":
        return render_template('cool.html', image_data=image_data)
    else:
        return "Could not determine the personal color."

if __name__ == '__main__':
    app.run(debug=True)
 