from flask import Flask, render_template, request, redirect, url_for

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

# 6. 결과 페이지 라우트 (설문 또는 사진 결과)
@app.route('/result')
def result():
    return render_template('result.html')  # 결과 페이지

if __name__ == '__main__':
    app.run(debug=True)
