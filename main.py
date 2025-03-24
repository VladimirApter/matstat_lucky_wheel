import pandas as pd
from flask import Flask, render_template, abort

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
        for row_idx in range(0, 13):
            try:
                row = df.iloc[row_idx]
                name = row.iloc[0]

                # Пропускаем студентов из списка исключений
                if name in StudentSelector.EXCLUDED_STUDENTS:
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

    @classmethod
    def prepare_students(cls, gid):
        students = cls.get_student_data(gid)
        if not students:
            return None
        return students


@app.route('/<group_name>')
def wheel_of_fortune(group_name):
    if group_name not in GROUPS:
        abort(404)

    gid = GROUPS[group_name]
    students = StudentSelector.prepare_students(gid)

    if students is None:
        return "Нет данных о студентах", 500

    formatted_students = [{
        "name": s['name'],
        "score": s['score']
    } for s in students]

    return render_template('wheel.html', students=formatted_students)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)