from flask import Flask, render_template

app = Flask(__name__)


# Функция из предыдущего решения (адаптированная)
def get_student_results():
    import pandas as pd

    url = "https://docs.google.com/spreadsheets/d/1QyIvnpMN1H3v6Ywj6QGl59KsdRbeUrtHXcAlE45sasY/export?format=csv&gid=1801994266"
    df = pd.read_csv(url)

    practice_columns = [9, 11, 13, 15, 17, 20, 24, 26, 29, 31, 33, 35]

    def safe_convert(value):
        try:
            value = str(value).lower().replace(',', '.').strip()
            return float(value) if value and value not in ['', 'н',
                                                           'nan'] else 0.0
        except:
            return 0.0

    results = []
    for row_idx in range(0, 13):
        try:
            row = df.iloc[row_idx]
            student_name = row.iloc[0]

            if student_name == "Артемьев Тимофей":
                continue

            total = sum(
                safe_convert(row.iloc[col]) for col in practice_columns)
            results.append({
                'name': student_name,
                'score': round(total, 2)
            })

        except Exception as e:
            print(f"Ошибка обработки строки {row_idx}: {str(e)}")

    return results


@app.route('/')
def show_results():
    students = get_student_results()
    return render_template('results.html', students=students)


if __name__ == '__main__':
    app.run(debug=True)