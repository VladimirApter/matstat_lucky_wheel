export function filterStudents(students) {
  return students.filter(student => {
    const checkbox = document.getElementById(`student-checkbox-${student.name}`);
    return !checkbox || !checkbox.checked;
  });
}
