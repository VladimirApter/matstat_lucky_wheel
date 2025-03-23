document.addEventListener('DOMContentLoaded', function () {
  const canvas = document.getElementById('wheelCanvas');
  const ctx = canvas.getContext('2d');
  const spinButton = document.getElementById('spinButton');
  const resultDiv = document.getElementById('result');

  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;
  const radius = Math.min(centerX, centerY) - 20;
  let rotation = 0;
  let isSpinning = false;

  // Расчёт углов сегментов (углы отсчитываются от правой стороны)
  const segments = [];
  let currentAngle = 0;
  students.forEach((student) => {
    const angle = (student.probability / 100) * 2 * Math.PI;
    segments.push({
      name: student.name,
      startAngle: currentAngle,
      endAngle: currentAngle + angle,
      // Цвет генерируется по схеме HSL, равномерно распределив оттенки:
      color: `hsl(${Math.floor(currentAngle * 180 / Math.PI)}, 70%, 60%)`
    });
    currentAngle += angle;
  });

  // Рисуем колесо с учетом текущей ротации
  function drawWheel() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    // Переносим начало координат в центр и вращаем колесо
    ctx.translate(centerX, centerY);
    ctx.rotate(rotation);

    segments.forEach((segment) => {
      // Рисуем сегмент
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.arc(0, 0, radius, segment.startAngle, segment.endAngle);
      ctx.closePath();
      ctx.fillStyle = segment.color;
      ctx.fill();
      ctx.strokeStyle = "#fff";
      ctx.stroke();

      // Рисуем текст сегмента вдоль радиуса (от центра к краю)
      const midAngle = (segment.startAngle + segment.endAngle) / 2;
      ctx.save();
      // Поворачиваем контекст по направлению сегмента
      ctx.rotate(midAngle);
      // Перемещаемся к точке, начиная от которой пишем текст
      ctx.translate(radius - 60, 0);
      // Текст рисуется по направлению радиуса (без дополнительного поворота)
      ctx.fillStyle = "#000";
      ctx.font = "14px Arial";
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.fillText(segment.name, 0, 0);
      ctx.restore();
    });
    ctx.restore();

    // Рисуем указатель, развернутый так, чтобы острая часть смотрела внутрь (влево)
    drawPointer();
  }

  function drawPointer() {
    ctx.fillStyle = "#e74c3c";
    ctx.beginPath();
    // Расчет координат для указателя:
    // Точка (tip) – на окружности, немного смещенная внутрь: здесь это (centerX + radius - 10, centerY)
    // Основание указателя – правее этой точки, чтобы треугольник указывал влево.
    const tipX = centerX + radius - 10;
    const tipY = centerY;
    const baseTopX = centerX + radius + 10;
    const baseTopY = centerY - 10;
    const baseBottomX = centerX + radius + 10;
    const baseBottomY = centerY + 10;
    ctx.moveTo(tipX, tipY);
    ctx.lineTo(baseTopX, baseTopY);
    ctx.lineTo(baseBottomX, baseBottomY);
    ctx.closePath();
    ctx.fill();
  }

  drawWheel();

  // Анимация вращения
  function spin() {
    if (isSpinning) return;
    isSpinning = true;
    resultDiv.textContent = "";

    // Случайное число оборотов от 5 до 8 и случайный угол
    const spins = Math.random() * 3 + 5; // от 5 до 8 оборотов
    const finalAngle = spins * 2 * Math.PI + Math.random() * 2 * Math.PI;
    const duration = 5000; // 5 секунд
    const start = performance.now();

    function animate(now) {
      const elapsed = now - start;
      if (elapsed < duration) {
        // Функция замедления (easeOut)
        const t = elapsed / duration;
        const eased = 1 - Math.pow(1 - t, 3);
        rotation = eased * finalAngle;
        drawWheel();
        requestAnimationFrame(animate);
      } else {
        rotation = finalAngle;
        drawWheel();
        isSpinning = false;
        determineWinner();
      }
    }

    requestAnimationFrame(animate);
  }

  // Определяем выбранного студента
  function determineWinner() {
    // Поскольку указатель находится справа (угол 0 в системе колеса),
    // угол указателя в системе колеса равен (-rotation) mod (2π)
    let pointerAngle = (-rotation) % (2 * Math.PI);
    if (pointerAngle < 0) pointerAngle += 2 * Math.PI;

    // Находим сегмент, в котором находится указанный угол
    const winningSegment = segments.find(seg => pointerAngle >= seg.startAngle && pointerAngle < seg.endAngle);
    resultDiv.textContent = winningSegment ? `Выбран: ${winningSegment.name}` : "Не удалось определить победителя";
  }

  spinButton.addEventListener('click', spin);
});
