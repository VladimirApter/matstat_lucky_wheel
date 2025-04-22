import pandas as pd
from flask import Flask, render_template, abort, jsonify
import threading
import random
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

    """
    <h3>📉 Анализ с юмором</h3>
    <div class="chat-log">
        <div><strong>#Ховрычев:</strong> Так, переходим к разделу "Однофакторный дисперсионный анализ"</div>
        <div><strong>С:</strong> Ну неет</div>
        <div><strong>#Мизурова:</strong> Я тебе говорю, он должен называться "Депрессионный"</div>
    </div>
    """,

    """
    <h3>🤔 Философия вопросов</h3>
    <div class="chat-log">
        <div>- Задайте уже вопрос, который надо задать</div>
        <div>- Ладно, я сам вас подведу к этому вопросу</div>
        <div>- Хотя нет, это уже ответ получается</div>
        <div>- Ну ладно, раз он у вас не возник, может и не надо рассказывать?</div>
        <div>- Или это я чересчур хорошо подготовился к паре?</div>
    </div>
    """,

    """
    <h3>🤯 За гранью понимания</h3>
    <div class="chat-log">
        <div>Человек в здравом уме такого не придумает и не расскажет</div>
    </div>
    """,

    """
    <h3>🔄 Вопросы из прошлого</h3>
    <div class="chat-log">
        <div><strong>#Ховрычев:</strong> Почему вы не задаете вопрос, который задали на прошлой паре</div>
        <div><strong>С:</strong> А в чем смысл?</div>
        <div><strong>#Ховрычев:</strong> Неет, не такой</div>
    </div>
    """,

    """
    <h3>🎭 Выдуманная реальность</h3>
    <div class="chat-log">
        <div><strong>#Ховрычев:</strong> Это задание нужно, чтобы вы убедились, что мы это все не мы выдумали</div>
        <div><strong>#Мизурова:</strong> А прикинь мы вообще все это выдумали и сейчас вам тут это рассказываем</div>
        <div><strong>#Ховрычев:</strong> Нуу, на самом деле я не все что рассказывал брал из учебников</div>
    </div>
    """,

    """
    <h3>⚰️ Задачи-гробы</h3>
    <div class="chat-log">
        <div>Ой что то я много гробов добавил. Надеюсь никто не будет их решать, а то наверное мне придется их проверять...</div>
    </div>
    """,

    """
    <h3>✏️ Исправление ошибок</h3>
    <div class="chat-log">
        <div>Мы должны дорешать эту задачу, потому что мы с прошлой группой неправильно решили, а я хочу узнать ответ</div>
    </div>
    """,

    """
    <h3>👨🏫 Наследие Колмогорова</h3>
    <div class="chat-log">
        <div>Решать задачу будет Колмогоров, а не мы</div>
    </div>
    """,

"""
    <h3>👮♂️ Военкомат vs Статистика</h3>
    <div class="chat-log">
        <div><strong>#Ховрычев:</strong> Мы же не можем поймать всех мужчин на улице и измерить</div>
        <div><strong>#Мизурова:</strong> Не согласна, военкомат может</div>
    </div>
    """,

    """
    <h3>🕺 Четверо мужиков и молоток</h3>
    <div class="chat-log">
        <div>Будет у нас 4 мужика, которыми мы будем пользоваться</div>
    </div>
    """,

    """
    <h3>🔢 Три слова или смерть</h3>
    <div class="chat-log">
        <div><strong>#Хлопин:</strong> Ответьте 3 словами, что такое фильтр Калмана. Я считать буду</div>
        <div><strong>С:</strong> Ну могу попробовать...</div>
        <div><strong>#Хлопин:</strong> Все, 3 слова сказано</div>
    </div>
    """,

    """
    <h3>😭 Ускоренный курс депрессии</h3>
    <div class="chat-log">
        <div>Я раньше вот этот материал за месяц рассказывал. так что если вам грустно, то это не случайно</div>
    </div>
    """,

    """
    <h3>🥾 Красота через пинки</h3>
    <div class="chat-log">
        <div>Я хочу чтобы мир был красивый. А если он вдруг не красивый, то надо запинать его ногами в красивый ящик</div>
    </div>
    """,

    """
    <h3>🦶 Оценка по пяткам</h3>
    <div class="chat-log">
        <div><strong>#Хлопин:</strong> баллы пусть Дмитрий выставляет. У меня оценка - диапазон от 1 до 10, в зависимости от левой пятки...</div>
        <div><strong>#Сенников:</strong> увы, у меня только правая пятка напряжена.</div>
        <div><strong>#Хлопин:</strong> ужасно.</div>
    </div>
    """,

    """
    <h3>💡 Гениальная тупость</h3>
    <div class="chat-log">
        <div>Уравнение 3 нам показывает что есть тупой изящный метод. Он одновременно и тупой и изящный, потому что настолько тупой, что аж изящный</div>
    </div>
    """,

    """
    <h3>🧠 Отрицательный склероз</h3>
    <div class="chat-log">
        <div><strong>С:</strong> А здесь можно брать K отрицательные?</div>
        <div><strong>#Хлопин:</strong> Ну никто не запрещал</div>
        <div><strong>С:</strong> А почему мы так не делаем?</div>
        <div><strong>#Хлопин:</strong> Забыл, склероз. Все, следующий вопрос</div>
    </div>
    """,

    """
    <h3>🎯 Оценка оценивает оценивание</h3>
    <div class="chat-log">
        <div><strong>C:</strong> Это же оценка, а что она оценивает?</div>
        <div><strong>#Хлопин:</strong> Ну дисперсию</div>
        <div><strong>C:</strong> Нет, ну как она ее оценивает?</div>
        <div><strong>#Хлопин:</strong> Ну, как может</div>
    </div>
    """,

    """
    <h3>🤐 Студенты получают по e-баллу</h3>
    <div class="chat-log">
        <div>Хотели дать 2 балла, но там появились 2 слайда без картинки, и мы решили что за такое надо дать по e-баллу, так что вот вам e-балл на двоих</div>
    </div>
    """,

    """
    <h3>🏆 Неотличный восторг</h3>
    <div class="chat-log">
        <div><strong>#Стахеев:</strong> Прямо хороший доклад</div>
        <div><strong>#Хлопин:</strong> Ну да, согласен, что не отличный</div>
    </div>
    """,
]


# Храним последний выданный индекс
last_index = {'value': -1}
lock = threading.Lock()


@app.route("/next-message")
def next_message():
    with lock:
        available_indices = list(range(len(MESSAGES)))

        # Удаляем последний выданный индекс из возможных вариантов
        if last_index['value'] in available_indices:
            available_indices.remove(last_index['value'])

        # Если все цитаты были использованы (для случая с 1 цитатой), разрешаем повтор
        if not available_indices:
            available_indices = list(range(len(MESSAGES)))

        new_index = random.choice(available_indices)
        last_index['value'] = new_index

    return jsonify({"message": MESSAGES[new_index]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)