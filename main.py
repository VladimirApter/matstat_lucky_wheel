import pandas as pd
from flask import Flask, render_template

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'your_secret_key_here'


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
        epsilon = 1e-8
        adjusted_scores = [s + epsilon for s in scores]
        inverted = [1 / (s + 0.01) for s in adjusted_scores]
        total = sum(inverted)

        probabilities = [w / total for w in inverted]
        probabilities[-1] += 1.0 - sum(probabilities)
        return [p / sum(probabilities) for p in probabilities]

    @classmethod
    def prepare_students(cls):
        students = cls.get_student_data()
        if not students:
            return None

        scores = [s['score'] for s in students]

        try:
            exact_probabilities = cls.calculate_probabilities(scores)
        except Exception as e:
            print(f"Ошибка расчета вероятностей: {e}")
            exact_probabilities = [1 / len(scores)] * len(scores)

        display_probabilities = [round(p * 100, 6) for p in
                                 exact_probabilities]

        # Корректировка суммы до 100%
        sum_display = sum(display_probabilities)
        display_probabilities[-1] += round(100 - sum_display, 6)

        for i, s in enumerate(students):
            s['probability'] = float(display_probabilities[i])

        return students


@app.route('/')
def wheel_of_fortune():
    students = StudentSelector.prepare_students()
    if students is None:
        return "Нет данных о студентах", 500

    formatted_students = [{
        "name": s['name'],
        "probability": s['probability']
    } for s in students]

    return render_template('wheel.html', students=formatted_students)


if __name__ == '__main__':
    app.run(debug=True)