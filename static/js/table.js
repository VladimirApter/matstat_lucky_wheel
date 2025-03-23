import { updateWheel } from "./main.js";

export function populateTable(students, wheel) {
  const tbody = document.getElementById("studentsTable").querySelector("tbody");
  tbody.innerHTML = "";

  students.forEach(student => {
    const tr = document.createElement("tr");

    // Проверяем, есть ли студент в колесе (если нет, он исключён)
    const segment = wheel.segments.find(seg => seg.name === student.name);
    if (!segment) tr.classList.add("inactive");

    // Цвет сегмента (если студент исключён, серый)
    const colorTd = document.createElement("td");
    const colorBox = document.createElement("div");
    colorBox.style.width = "20px";
    colorBox.style.height = "20px";
    colorBox.style.backgroundColor = student.color;
    colorTd.appendChild(colorBox);

    // Вероятность (если студент отсутствует, показываем 0%)
    const chanceTd = document.createElement("td");
    chanceTd.textContent = segment ? segment.probability.toFixed(6) : "0.000000";

    // Имя студента
    const nameTd = document.createElement("td");
    nameTd.textContent = student.name;

    // Чекбокс для исключения из колеса
    const checkboxTd = document.createElement("td");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.id = `student-checkbox-${student.name}`;
    checkbox.checked = !segment; // Если сегмента нет, значит студент уже отмечен отсутствующим
    checkbox.addEventListener("change", updateWheel);
    checkboxTd.appendChild(checkbox);

    tr.appendChild(colorTd);
    tr.appendChild(chanceTd);
    tr.appendChild(nameTd);
    tr.appendChild(checkboxTd);
    tbody.appendChild(tr);
  });
}

// Функция получения списка исключенных студентов
export function getExcludedStudents() {
  return students
    .filter(student => {
      const checkbox = document.getElementById(`student-checkbox-${student.name}`);
      return checkbox && checkbox.checked;
    })
    .map(student => student.name);
}
