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

  // Константы для анимации (в миллисекундах и радиан/мс)
  const ACCEL_DURATION = 1500;      // фаза разгона
  const DECEL_DURATION = 10000;      // фаза торможения
  const CONST_DURATION_MAX = 3000;  // максимум времени равномерного вращения
  const MAX_SPEED = 0.015;          // максимальная скорость (рад/мс)

  // Расчёт углов сегментов (начинаем отсчет от правой стороны)
  const segments = [];
  let currentAngle = 0;
  students.forEach((student) => {
    const angle = (student.probability / 100) * 2 * Math.PI;
    segments.push({
      name: student.name,
      probability: student.probability, // для таблицы
      startAngle: currentAngle,
      endAngle: currentAngle + angle,
      // Цвет вычисляется по схеме HSL, равномерно распределяя оттенки:
      color: `hsl(${Math.floor(currentAngle * 180 / Math.PI)}, 70%, 60%)`
    });
    currentAngle += angle;
  });

  // Заполнение таблицы студентов
  function populateTable() {
    const tbody = document.getElementById('studentsTable').querySelector('tbody');
    tbody.innerHTML = '';
    segments.forEach(segment => {
      const tr = document.createElement('tr');

      const colorTd = document.createElement('td');
      const colorBox = document.createElement('div');
      colorBox.style.width = '20px';
      colorBox.style.height = '20px';
      colorBox.style.backgroundColor = segment.color;
      colorTd.appendChild(colorBox);

      const chanceTd = document.createElement('td');
      chanceTd.textContent = segment.probability.toFixed(6);

      const nameTd = document.createElement('td');
      nameTd.textContent = segment.name;

      tr.appendChild(colorTd);
      tr.appendChild(chanceTd);
      tr.appendChild(nameTd);
      tbody.appendChild(tr);
    });
  }

  populateTable();

  // Рисуем колесо с учетом текущей ротации
  function drawWheel() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
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
      ctx.rotate(midAngle);
      ctx.translate(radius * 0.7, 0); // смещение по радиусу
      ctx.fillStyle = "#000";
      ctx.font = "16px Arial";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(segment.name, 0, 0);
      ctx.restore();
    });
    ctx.restore();

    // Отрисовка указателя
    drawPointer();
  }

  // Указатель расположен справа от колеса и развернут так, чтобы его острая часть смотрела влево (внутрь)
  function drawPointer() {
    ctx.fillStyle = "#e74c3c";
    ctx.beginPath();
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

  // Анимация вращения по фазам
  function spin() {
    if (isSpinning) return;
    isSpinning = true;
    resultDiv.textContent = "";
    rotation = 0; // сброс вращения для нового запуска

    // Фаза равномерного вращения: случайное время от 0 до CONST_DURATION_MAX
    const constantPhaseTime = Math.random() * CONST_DURATION_MAX;
    const totalDuration = ACCEL_DURATION + constantPhaseTime + DECEL_DURATION;

    const startTime = performance.now();
    let lastTime = startTime;

    function animate(now) {
      const elapsed = now - startTime;
      const dt = now - lastTime; // время с предыдущего кадра
      let currentSpeed = 0;

      if (elapsed < ACCEL_DURATION) {
        // Фаза разгона (линейное ускорение)
        const factor = elapsed / ACCEL_DURATION;
        currentSpeed = MAX_SPEED * factor;
      } else if (elapsed < ACCEL_DURATION + constantPhaseTime) {
        // Фаза равномерного вращения (константная скорость)
        currentSpeed = MAX_SPEED;
      } else if (elapsed < totalDuration) {
        // Фаза торможения (квадратичный ease-out)
        const tDecel = elapsed - ACCEL_DURATION - constantPhaseTime;
        const factor = tDecel / DECEL_DURATION; // от 0 до 1
        // При factor=0: скорость = MAX_SPEED, при factor=1: скорость = 0
        currentSpeed = MAX_SPEED * (1 - Math.pow(factor, 2));
      } else {
        // Завершаем анимацию: гарантированно останавливаем колесо
        isSpinning = false;
        drawWheel();
        determineWinner();
        return;
      }

      rotation += currentSpeed * dt;
      lastTime = now;
      drawWheel();
      requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
  }

  // Определяем выбранного студента
  function determineWinner() {
    // Указатель находится справа (угол 0 в системе колеса)
    let pointerAngle = (-rotation) % (2 * Math.PI);
    if (pointerAngle < 0) pointerAngle += 2 * Math.PI;

    const winningSegment = segments.find(seg => pointerAngle >= seg.startAngle && pointerAngle < seg.endAngle);
    resultDiv.textContent = winningSegment ? `Выбран: ${winningSegment.name}` : "Не удалось определить победителя";
  }

  spinButton.addEventListener('click', spin);
});
