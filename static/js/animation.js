import { markStudentAsChosen } from "./table.js";

export function startSpin(wheel) {
  const spinButton = document.getElementById("spinButton");
  spinButton.disabled = true; // Отключаем кнопку

  const resultDiv = document.getElementById("result");
  resultDiv.textContent = "К доске пойдёёёёт";
  let dotState = 0;
  const ellipsisInterval = setInterval(() => {
    dotState = (dotState + 1) % 4;
    let dots = ".".repeat(dotState);
    resultDiv.textContent = "К доске пойдёёёёт" + dots;
  }, 500);

  const { drawWheel, segments } = wheel;
  let rotation = 0;
  let isSpinning = true;

  const ACCEL_DURATION = 1500;
  const DECEL_DURATION = 10000;
  const CONST_DURATION_MAX = 4000;
  const MAX_SPEED = 0.015;

  const constantPhaseTime = Math.random() * CONST_DURATION_MAX;
  const totalDuration = ACCEL_DURATION + constantPhaseTime + DECEL_DURATION;

  const startTime = performance.now();
  let lastTime = startTime;

  function animate(now) {
    const elapsed = now - startTime;
    const dt = now - lastTime;
    let currentSpeed = 0;

    if (elapsed < ACCEL_DURATION) {
      currentSpeed = MAX_SPEED * (elapsed / ACCEL_DURATION);
    } else if (elapsed < ACCEL_DURATION + constantPhaseTime) {
      currentSpeed = MAX_SPEED;
    } else if (elapsed < totalDuration) {
      const tDecel = elapsed - ACCEL_DURATION - constantPhaseTime;
      const k = 5;
      currentSpeed = MAX_SPEED * Math.exp(-k * (tDecel / DECEL_DURATION));
    } else {
      isSpinning = false;
      clearInterval(ellipsisInterval); // Останавливаем анимацию троеточия
      determineWinner(rotation, segments);
      spinButton.disabled = false; // Включаем кнопку после завершения
      return;
    }

    rotation += currentSpeed * dt;
    lastTime = now;
    drawWheel(rotation);
    requestAnimationFrame(animate);
  }

  requestAnimationFrame(animate);
}

function determineWinner(rotation, segments) {
  let pointerAngle = (-rotation) % (2 * Math.PI);
  if (pointerAngle < 0) pointerAngle += 2 * Math.PI;

  const winningSegment = segments.find(seg => pointerAngle >= seg.startAngle && pointerAngle < seg.endAngle);
  const resultDiv = document.getElementById("result");
  if (winningSegment) {
    resultDiv.textContent = `К доске пойдёёёёт ${winningSegment.name} 🎉`;
    setTimeout(() => {
      markStudentAsChosen(winningSegment.name);
    }, 5500);
  }
}
