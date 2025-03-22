import pandas as pd

url = "https://docs.google.com/spreadsheets/d/1QyIvnpMN1H3v6Ywj6QGl59KsdRbeUrtHXcAlE45sasY/export?format=csv&gid=1801994266"
df = pd.read_csv(url)

# Определяем правильные индексы столбцов на основе вашего вывода
practice_columns = [
    9,  # 12.02
    11,  # 19.02
    13,  # 26.2
    15,  # 5.3
    17,  # 12.3
    20,  # 26.03
    24,  # 9.4
    26,  # 16.4
    29,  # 30.04
    31,  # 07.05
    33,  # 14.05
    35,  # 21.5
]


def safe_convert(value):
    try:
        value = str(value).lower().replace(',', '.').strip()
        if value in ['', 'н', 'nan', 'none']:
            return 0.0
        return float(value)
    except:
        return 0.0


results = []
for row_idx in range(0, 13):  # Строки 1-13 исходной таблицы (0-12 в Pandas)
    try:
        row = df.iloc[row_idx]
        student_name = row.iloc[0] if pd.notna(row.iloc[0]) else "Неизвестный"

        # Пропускаем студента с именем "Артемьев Тимофей"
        if student_name == "Артемьев Тимофей":
            continue

        total = 0.0
        for col_idx in practice_columns:
            try:
                value = row.iloc[col_idx]
                total += safe_convert(value)
            except IndexError:
                continue  # Пропускаем отсутствующие столбцы

        results.append((student_name, round(total, 2)))

    except Exception as e:
        print(f"Ошибка в строке {row_idx + 1}: {str(e)}")
        results.append(("Ошибка в данных", 0.0))

print("\nРезультаты:")
for name, score in results:
    print(f"{name}: {score}")