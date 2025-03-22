from flask import Flask, render_template
import pandas as pd
import numpy as np

app = Flask(__name__)


def calculate_probabilities(scores):
    # Инвертируем баллы с защитой от нуля
    inverted = [1 / (score + 0.01) for score in
                scores]  # +0.01 для стабильности

    # Нормализуем до суммы 1
    total = sum(inverted)
    probabilities = [w / total for w in inverted]

    # Корректируем сумму из-за погрешности вычислений
    probabilities[-1] += 1.0 - sum(probabilities)
    return probabilities


def get_student_data():
    url = "https://docs.google.com/spreadsheets/d/1QyIvnpMN1H3v6Ywj6QGl59KsdRbeUrtHXcAlE45sasY/export?format=csv&gid=1801994266"
    df = pd.read_csv(url)

    practice_columns = [9, 11, 13, 15, 17, 20, 24, 26, 29, 31, 33, 35]

    students = []
    for row_idx in range(0, 13):
        try:
            row = df.iloc[row_idx]
            name = row.iloc[0]

            if name == "Артемьев Тимофей":
                continue

            total = sum(
                float(str(val).replace(',', '.')) if str(val).replace(',',
                                                                      '').replace(
                    '.', '').isdigit() else 0.0
                for val in row.iloc[practice_columns]
            )
            students.append({
                'name': name,
                'score': round(total, 2)
            })

        except Exception as e:
            print(f"Ошибка в строке {row_idx}: {e}")

    return students


@app.route('/')
def wheel_of_fortune():
    students = get_student_data()

    if not students:
        return "Нет данных о студентах", 500

    # Получаем баллы и имена
    scores = [s['score'] for s in students]
    names = [s['name'] for s in students]

    # Рассчитываем точные вероятности
    try:
        exact_probabilities = calculate_probabilities(scores)
    except ZeroDivisionError:
        exact_probabilities = [1 / len(scores)] * len(scores)

    # Рассчитываем отображаемые проценты
    display_probabilities = [round(p * 100, 2) for p in exact_probabilities]

    # Выбираем победителя
    winner = np.random.choice(names, p=exact_probabilities)

    # Добавляем данные для отображения
    for i, s in enumerate(students):
        s['probability'] = display_probabilities[i]
        s['is_winner'] = (s['name'] == winner)

    return render_template('wheel.html', students=students)


if __name__ == '__main__':
    app.run(debug=True)