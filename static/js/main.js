import { computeProbabilities } from "./probabilities.js";
import { setupWheel } from "./wheel.js";
import { startSpin } from "./animation.js";
import { populateTable, getExcludedStudents } from "./table.js";

let wheel;

document.addEventListener("DOMContentLoaded", function () {
  updateWheel();
  document.getElementById("spinButton").addEventListener("click", () => startSpin(wheel));
});

// Функция обновления колеса при изменении списка студентов
export function updateWheel() {
  const excludedStudents = getExcludedStudents();
  const activeStudents = students.filter(s => !excludedStudents.includes(s.name));

  if (activeStudents.length === 0) {
    document.getElementById("result").textContent = "Все студенты отсутствуют!";
    return;
  }

  const probs = computeProbabilities(activeStudents);
  activeStudents.forEach((student, idx) => student.probability = probs[idx] * 100);

  wheel = setupWheel(activeStudents);
  populateTable(students, wheel);
}
