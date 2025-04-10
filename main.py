import pandas as pd
from flask import Flask, render_template, abort, jsonify
import threading
from livereload import Server

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'your_secret_key_here'

GROUPS = {
    'ft-201-1': '0',
    'ft-201-2': '313135890',
    'ft-202-1': '429115037',
    'ft-202-2': '1499384932',
    'ft-203-1': '1434241927',
    'ft-203-2': '101485156',
    'ft-204-1': '1801994266',
    'ft-204-2': '2063966210',
    'kn': '393945752'
}

GROUPS_COUNT ={
    '0': 14,
    '313135890' : 14,
    '429115037' : 15,
    '1499384932' : 15,
    '1434241927' : 13,
    '101485156' : 13,
    '1801994266': 13,
    '2063966210': 14,
    '393945752': 4,
}

class StudentSelector:
    EXCLUDED_STUDENTS = {
        "Бутовой Владислав",
        "Гальянов Фёдор",
        "Бархатова Алёна",
        "Пузынин Георгий",
        "Сидорова Алёна",
        "Одайкина Елизавета",
        "Юдин Николай",
        "Артемьев Тимофей",
        "Колесников Захар",
        "Печников Георгий",
        "Сахбиев Марат",
        "Суставов Данил Сергеевич"
    }

    @staticmethod
    def get_student_data(gid):
        url = f"https://docs.google.com/spreadsheets/d/1QyIvnpMN1H3v6Ywj6QGl59KsdRbeUrtHXcAlE45sasY/export?format=csv&gid={gid}"
        df = pd.read_csv(url)

        practice_columns = [9, 11, 13, 15, 17, 20, 24, 26, 29, 31, 33, 35]

        students = []
        for row_idx in range(GROUPS_COUNT[gid]):
            try:
                row = df.iloc[row_idx]
                name = row.iloc[0]

                # Пропускаем студентов из списка исключений
                if name in StudentSelector.EXCLUDED_STUDENTS:
                    continue

                total = sum(
                    float(str(val).replace(',', '.')) if str(val).replace(',', '').replace('.', '').isdigit() else 0.0
                    for val in row.iloc[practice_columns]
                )

                students.append({
                    'name': name,
                    'score': round(total, 2)
                })

            except Exception as e:
                print(f"Ошибка в строке {row_idx}: {e}")

        return students


@app.route('/<group_name>')
def wheel_of_fortune(group_name):
    if group_name not in GROUPS:
        abort(404)

    gid = GROUPS[group_name]
    students = StudentSelector.get_student_data(gid)

    if students is None:
        return "Нет данных о студентах", 500

    formatted_students = [{
        "name": s['name'],
        "score": s['score']
    } for s in students]

    return render_template('wheel.html', students=formatted_students)


@app.route('/')
def main_page():
    return render_template('main.html')

MESSAGES = [
    """
    <h3>🧠 Беседа мегамозгов</h3>
    <div class="chat-log">
        <div><strong>#Ховрычев:</strong> Где мой любимый коричневый маркер?</div>
        <div><strong>#Мизурова:</strong> Для контекста, Андрей на первой паре взял коричневый маркер и стал смеяться</div>
        <div><strong>#Ховрычев:</strong> Ну а что, я еще никогда не видел коричневых</div>
        <div><strong>#Мизурова:</strong> А маркеры?</div>
    </div>
    """,

    """
    <h3>📚 Теоретические размышления</h3>
    <div class="chat-log">
        <div><strong>С:</strong> А что значит вот эта вот запись в скобочках в теории?</div>
        <div><strong>#Ховрычев:</strong> Так, это я писал. А зачем я это написал?</div>
    </div>
    """,

    """
    <h3>📊 Статистика по-ховрычевски</h3>
    <div class="chat-log">
        <div><strong>#Ховрычев:</strong> Эта статистика строится вот так</div>
        <div><strong>С:</strong> А почему так?</div>
        <div><strong>#Ховрычев:</strong> Это хороший вопрос. Можете дома разобраться и мне потом объяснить</div>
    </div>
    """,

    """
    <h3>🤖 Советы будущего</h3>
    <div class="chat-log">
        <div>Могли бы уже давно в ChatGPT забить. Сидят тут что-то, думают</div>
    </div>
    """,

    """
    <h3>🧠 Сложная задачка</h3>
    <div class="chat-log">
        <div>Это задачка сложная для понимания, поэтому посмотрите ее еще раз дома...</div>
        <div><em>*Начинает смеяться*</em></div>
    </div>
    """,

    """
    <h3>🧠 Память студента</h3>
    <div class="chat-log">
        <div>Классно, что ты это помнишь. Хотя вообще-то все должны это помнить</div>
    </div>
    """,

    """
    <h3>🌙 Ночь, спиннер и математика</h3>
    <div class="chat-log">
        <div><strong>А:</strong> Я не спал всю ночь и читал интересные факты, связанные с математикой. Вы знали, что человек гомеоморфен спиннеру?</div>
    </div>
    """,

    """
    <h3>🧑‍🏫 Сам себе объяснил</h3>
    <div class="chat-log">
        <div><strong>#Ховрычев:</strong> Не ну я считаю что я для себя прямо хорошо объяснил</div>
        <div><strong>С:</strong> Ну главное что ты понял</div>
    </div>
    """,
]


# Shared index with a lock for thread safety
message_index = {'value': 0}
lock = threading.Lock()

@app.route("/next-message")
def next_message():
    with lock:
        index = message_index['value']
        message = MESSAGES[index]
        # Update for next request (loop back to 0)
        message_index['value'] = (index + 1) % len(MESSAGES)
    return jsonify({"message": message})


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000)
    server = Server(app.wsgi_app)
    server.watch('static/')
    server.watch('templates/')
    server.serve()
