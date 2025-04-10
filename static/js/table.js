import { updateWheel } from "./main.js";

export function populateTable(students, wheel) {
  const tbody = document.getElementById("studentsTable").querySelector("tbody");
  tbody.innerHTML = "";

  students.forEach(student => {
    const tr = document.createElement("tr");

    // Проверяем, есть ли студент в колесе (если нет, он исключён)
    const segment = wheel.segments.find(seg => seg.name === student.name);
    if (!segment) tr.classList.add("inactive");

    // Цвет сегмента (если студент исключён, остаётся прежним, но в таблице отображается через стиль inactive)
    const colorTd = document.createElement("td");
    const colorBox = document.createElement("div");
    colorBox.style.backgroundColor = student.color;
    colorTd.appendChild(colorBox);

    // Вероятность (округление до 2 знаков)
    const chanceTd = document.createElement("td");
    chanceTd.textContent = segment ? segment.probability.toFixed(2) + "%" : "0.00%";

    // Имя студента
    const nameTd = document.createElement("td");
    nameTd.classList.add("name");
    nameTd.textContent = student.name;
    nameTd.setAttribute("title", student.name);

    // Чекбокс для исключения
    const checkboxTd = document.createElement("td");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.id = `student-checkbox-${student.name}`;
    checkbox.checked = !segment;
    checkbox.addEventListener("change", updateWheel);
    checkboxTd.appendChild(checkbox);

    tr.appendChild(colorTd);
    tr.appendChild(chanceTd);
    tr.appendChild(nameTd);
    tr.appendChild(checkboxTd);
    tbody.appendChild(tr);
  });
}

export function getExcludedStudents() {
  return students
    .filter(student => {
      const checkbox = document.getElementById(`student-checkbox-${student.name}`);
      return checkbox && checkbox.checked;
    })
    .map(student => student.name);
}

export function markStudentAsChosen(name) {
  const checkbox = document.getElementById(`student-checkbox-${name}`);
  if (checkbox) {
    checkbox.checked = true;
    updateWheel();
  }
}
