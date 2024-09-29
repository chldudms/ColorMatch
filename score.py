from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 초기 설정: 세션에 점수 저장
@app.route('/')
def index():
    session['total_score'] = 0  # 초기 점수 설정
    return render_template('survey.html')  # 질문 시트 페이지 렌더링

# 사용자가 선택한 점수를 받는 엔드포인트
@app.route('/submit', methods=['POST'])
def submit_score():
    data = request.get_json()
    score = int(data.get('score'))
    
    # 세션에 점수 누적
    session['total_score'] += score
    
    return jsonify({'message': 'Score added successfully'}), 200

# 결과 페이지
@app.route('/result')
def result():
    total_score = session.get('total_score', 0)  # 세션에서 누적 점수 가져오기
    
    # 점수에 따라 결과 결정
    if total_score >= 20:
        result_message = "쿨톤"
    elif total_score >= 19:
        result_message = "웜톤" 
    else:
        result_message = "뉴트럴톤"

    return render_template('chapture.html', result=result_message, total_score=total_score)

 
if __name__ == '__main__':
    app.run(debug=True)