import pandas as pd
import numpy as np
from flask import Flask, render_template, request, session, jsonify
from colours import Color

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'your_secret_key_here'

# После создания экземпляра app
@app.template_filter('darker')
def darker_filter(color_hex, amount=0.2):
    color = Color(hex_code=color_hex)
    return color.darker(amount).hex

class StudentSelector:
    @staticmethod
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

    @staticmethod
    def calculate_probabilities(scores):
        # Защита от нулевых баллов
        epsilon = 1e-8
        adjusted_scores = [s + epsilon for s in scores]

        # Инвертируем баллы
        inverted = [1 / (s + 0.01) for s in adjusted_scores]
        total = sum(inverted)

        # Нормализуем с точной коррекцией
        probabilities = [w / total for w in inverted]
        probabilities[-1] += 1.0 - sum(probabilities)

        # Финализируем сумму
        return [p / sum(probabilities) for p in probabilities]

    @classmethod
    def prepare_students(cls):
        students = cls.get_student_data()
        if not students:
            return None

        scores = [s['score'] for s in students]

        try:
            probabilities = cls.calculate_probabilities(scores)
        except Exception as e:
            print(f"Ошибка расчета вероятностей: {e}")
            probabilities = [1 / len(scores)] * len(scores)

        exact_probabilities = [p / sum(probabilities) for p in probabilities]
        exact_probabilities[-1] += 1.0 - sum(exact_probabilities)

        # Отображаемые вероятности
        display_probabilities = [round(p * 100, 2) for p in
                                 exact_probabilities]

        # Корректировка суммы отображения
        sum_display = sum(display_probabilities)
        display_probabilities[-1] += 100 - sum_display

        for i, s in enumerate(students):
            s['exact_probability'] = exact_probabilities[
                                         i] * 100  # Для расчетов
            s['probability'] = display_probabilities[i]  # Для отображения

            hue = i * (360 / len(students))
            color = Color(hsl=(hue, 0.7, 0.5))
            s['color'] = color.hex
            s['wheel_color'] = color.hex  # Добавляем отдельное поле для колеса
            s['border_color'] = color.darker(0.2).hex

        return students

    @classmethod
    def select_winner(cls, students):
        names = [s['name'] for s in students]
        probabilities = [s['probability'] / 100 for s in students]

        # Точная нормализация
        sum_probs = sum(probabilities)
        normalized = [p / sum_probs for p in probabilities]

        return np.random.choice(names, p=normalized)

    @classmethod
    def calculate_target_angle(cls, students, winner_name):
        """Рассчитывает угол поворота для анимации колеса"""
        total_probability = sum(s['probability'] for s in students)
        accumulated = 0
        winner_index = 0

        for i, student in enumerate(students):
            if student['name'] == winner_name:
                winner_index = i
                break
            accumulated += student['probability']

        segment_angle = 360 * (
                    students[winner_index]['probability'] / total_probability)
        target_angle = 5 * 360 + (
                    360 - (accumulated + segment_angle / 2)) % 360
        return target_angle


@app.route('/', methods=['GET', 'POST'])
def wheel_of_fortune():
    students = StudentSelector.prepare_students()

    if students is None:
        return jsonify(error="Нет данных о студентах"), 500

    if request.method == 'POST':
        try:
            winner = StudentSelector.select_winner(students)
            session['winner'] = winner
            target_angle = StudentSelector.calculate_target_angle(students,
                                                                  winner)
            return jsonify({
                'winner': winner,
                'target_angle': target_angle,
                'students': students
            })
        except Exception as e:
            return jsonify(error=str(e)), 500

    current_winner = session.get('winner')
    for s in students:
        s['is_winner'] = (s['name'] == current_winner)

    return render_template('wheel.html', students=students)


if __name__ == '__main__':
    app.run(debug=True)