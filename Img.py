from flask import Flask, render_template, request, jsonify, redirect, url_for
import base64
import io
from PIL import Image

app = Flask(__name__)

# 피부톤 분석 함수 (임의의 로직)
def analyze_skin_tone(image_data):
    # 피부톤 분석 로직 (여기서 분석 로직을 수정할 수 있습니다.)
    return "봄"  # 예시로 봄으로 고정

@app.route('/')
def index():
    return render_template('chapture.html')

@app.route('/analyze_skin', methods=['POST'])
def analyze_skin():
    data = request.get_json()
    user_image = data.get('image')

    # Base64 이미지 데이터 처리
    image_data = user_image.split(',')[1]  # 'data:image/png;base64,' 제거
    image_bytes = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_bytes))

    # 피부톤 분석
    skin_tone = analyze_skin_tone(user_image)

    return jsonify({
        'skin_tone': skin_tone,
        'user_image': user_image  # 원본 이미지 데이터 반환
    })

@app.route('/result')
def result():
    # 결과 페이지는 JS에서 URL로 전송한 데이터로 표시됨
    return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True)
