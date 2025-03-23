export function setupWheel(students) {
  const canvas = document.getElementById("wheelCanvas");
  const ctx = canvas.getContext("2d");
  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;
  const radius = Math.min(centerX, centerY) - 20;

  let currentAngle = 0;
  const segments = students.map((student) => {
    const angle = (student.probability / 100) * 2 * Math.PI;
    const segment = {
      name: student.name,
      probability: student.probability,
      startAngle: currentAngle,
      endAngle: currentAngle + angle,
      color: `hsl(${Math.floor(currentAngle * 180 / Math.PI)}, 70%, 60%)`
    };
    currentAngle += angle;
    return segment;
  });

  function drawWheel(rotation = 0) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.translate(centerX, centerY);
    ctx.rotate(rotation);

    segments.forEach(segment => {
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.arc(0, 0, radius, segment.startAngle, segment.endAngle);
      ctx.closePath();
      ctx.fillStyle = segment.color;
      ctx.fill();
      ctx.strokeStyle = "#fff";
      ctx.stroke();

      const midAngle = (segment.startAngle + segment.endAngle) / 2;
      ctx.save();
      ctx.rotate(midAngle);
      ctx.translate(radius * 0.7, 0);
      ctx.fillStyle = "#000";
      ctx.font = "16px Arial";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(segment.name, 0, 0);
      ctx.restore();
    });

    ctx.restore();
    drawPointer();
  }

  function drawPointer() {
    ctx.fillStyle = "#e74c3c";
    ctx.beginPath();
    const tipX = centerX + radius - 10;
    const tipY = centerY;
    const baseX = centerX + radius + 10;
    ctx.moveTo(tipX, tipY);
    ctx.lineTo(baseX, tipY - 10);
    ctx.lineTo(baseX, tipY + 10);
    ctx.closePath();
    ctx.fill();
  }

  drawWheel();
  return { canvas, drawWheel, segments };
}
