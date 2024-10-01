from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('survey.html')  # 설문 페이지 로드

@app.route('/submit', methods=['POST'])
def submit():
    # 클라이언트에서 받은 총 점수
    data = request.get_json()  # JSON 형식으로 데이터를 받음
    total_score = data.get('total_score')

    # 점수에 따른 리디렉션
    if total_score >= 20:
        return jsonify({'redirect': url_for('cool_tone')})
    elif total_score >= 15:
        return jsonify({'redirect': url_for('warm_tone')})
    else:
        return jsonify({'redirect': url_for('neutral_tone')})

@app.route('/cool-tone')
def cool_tone():
    return render_template('result.html')  # 쿨톤 결과 페이지

@app.route('/warm-tone')
def warm_tone():
    return render_template('result.html')  # 웜톤 결과 페이지

@app.route('/neutral-tone')
def neutral_tone():
    return render_template('result.html')  # 뉴트럴 결과 페이지

if __name__ == '__main__':
    app.run(debug=True)
