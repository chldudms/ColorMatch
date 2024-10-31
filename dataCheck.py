import random
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 계절 톤을 랜덤으로 결정하는 함수
def analyze_skin_tone():
    seasons = ['겨울 쿨톤', '여름 쿨톤', '봄 웜톤', '가을 웜톤']
    return random.choice(seasons)

# 캡처 페이지 렌더링
@app.route('/chapture')
def chapture():
    return render_template('chapture.html')

# 사진을 받고 계절 톤을 분석하는 엔드포인트
@app.route('/analyze_skin', methods=['POST'])
def analyze_skin():
    # 이미지 데이터 수신 (프론트엔드에서 보내온 데이터 처리)
    image_data = request.form.get('image_data')  # 이미지 데이터

    # 세션에 이미지 저장
    session['captured_image'] = image_data

    # 랜덤으로 계절 톤 결정
    season = analyze_skin_tone()
    session['season'] = season

    # 결과 페이지로 리다이렉트
    return redirect(url_for('result1.html'))

# 결과 페이지 렌더링
@app.route('/result')
def result():
    # 세션에서 사진, 계절 톤 정보 가져오기
    captured_image = session.get('captured_image', None)
    season = session.get('season', '결정되지 않음')

    # 결과 페이지 렌더링
    return render_template('result.html', image=captured_image, season=season)

if __name__ == '__main__':
    app.run(debug=True)
