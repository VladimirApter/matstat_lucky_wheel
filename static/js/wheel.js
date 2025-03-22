let isSpinning = false;
let currentRotation = 0;

function initWheel() {
    const wheel = document.getElementById('wheel');
    wheel.innerHTML = '';

    const total = students.reduce((sum, s) => sum + s.exact_probability, 0);
    let accumulatedAngle = 0;

    students.forEach((student, index) => {
        const segment = document.createElement('div');
        segment.className = 'segment';
        const angle = (student.exact_probability / 100) * 360;

        // Основной сегмент
        segment.style.transform = `rotate(${accumulatedAngle}deg)`;
        segment.style.backgroundColor = student.wheel_color;

        // Точная граница сегмента
        segment.style.clipPath = index === students.length - 1
            ? 'polygon(50% 50%, 50% 0, 100% 0, 100% 100%, 50% 100%)'
            : 'polygon(50% 50%, 50% 0, 100% 0)';

        // Текст
        const text = document.createElement('div');
        text.className = 'segment-text';
        text.textContent = student.name;
        text.style.transform = `rotate(${angle/2}deg)`;
        text.style.color = getContrastColor(student.wheel_color);  // Функция контрастного текста

        segment.appendChild(text);
        wheel.appendChild(segment);

        accumulatedAngle += angle;
    });
}

// Функция для определения контрастного цвета текста
function getContrastColor(hexColor) {
    const r = parseInt(hexColor.substr(1,2), 16);
    const g = parseInt(hexColor.substr(3,2), 16);
    const b = parseInt(hexColor.substr(5,2), 16);
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    return luminance > 0.5 ? '#000000' : '#ffffff';
}

async function startSpin() {
    if (isSpinning) return;
    isSpinning = true;
    document.getElementById('spinButton').disabled = true;
    const resultElement = document.getElementById('result');
    resultElement.textContent = '';

    try {
        const response = await fetch('/', { method: 'POST' });
        if (!response.ok) throw new Error('Ошибка сервера');

        const data = await response.json();
        if (data.error) throw new Error(data.error);

        animateWheel(data.target_angle);
        showResult(data.winner);
    } catch (error) {
        resultElement.textContent = `Ошибка: ${error.message}`;
        console.error('Ошибка:', error);
    } finally {
        isSpinning = false;
        document.getElementById('spinButton').disabled = false;
    }
}

function animateWheel(targetAngle) {
    const wheel = document.getElementById('wheel');
    wheel.style.transition = 'transform 5s cubic-bezier(0.25, 0.1, 0.25, 1)';
    wheel.style.transform = `rotate(${currentRotation + targetAngle}deg)`;
    currentRotation = (currentRotation + targetAngle) % 360;
}

function showResult(winnerName) {
    const resultElement = document.getElementById('result');
    setTimeout(() => {
        resultElement.innerHTML = `🎉 Победитель: ${winnerName}! 🎉`;
    }, 5000);
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', initWheel);