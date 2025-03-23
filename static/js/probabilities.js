export function computeProbabilities(students) {
  const epsilon = 1e-8;
  const adjusted = students.map(s => s.score + epsilon);
  const inverted = adjusted.map(score => 1 / (score + 0.01));
  const total = inverted.reduce((acc, val) => acc + val, 0);

  let probabilities = inverted.map(val => val / total);
  probabilities[probabilities.length - 1] += 1 - probabilities.reduce((acc, val) => acc + val, 0);

  return probabilities.map(val => val / probabilities.reduce((acc, val) => acc + val, 0));
}
