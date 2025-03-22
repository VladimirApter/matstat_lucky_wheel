// Инициализация переменных
let spinning = false;
let rotation = 0;
const rotations = 5;
let students = window.students;

// Генерация цветов
students.forEach((student, index) => {
    const hue = (index * 360 / students.length) % 360;
    student.color = `hsl(${hue}, 70%, 50%)`;
});

// Инициализация колеса
const canvas = document.getElementById('wheel');
const ctx = canvas.getContext('2d');
const center = canvas.width / 2;
const radius = canvas.width / 2 - 20;

function drawWheel() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    let startAngle = -Math.PI/2;

    students.forEach(student => {
        const angle = (student.probability / 100) * 2 * Math.PI;

        // Рисуем сегмент
        ctx.beginPath();
        ctx.moveTo(center, center);
        ctx.arc(center, center, radius, startAngle, startAngle + angle);
        ctx.fillStyle = student.color;
        ctx.fill();

        // Текст
        ctx.save();
        ctx.translate(center, center);
        ctx.rotate(startAngle + angle/2);
        ctx.fillStyle = 'white';
        ctx.font = '14px Arial';
        ctx.textAlign = 'right';
        ctx.fillText(student.name, radius - 10, 5);
        ctx.restore();

        startAngle += angle;
    });
}

function getWinnerIndex() {
    const total = students.reduce((sum, s) => sum + s.probability, 0);
    const random = Math.random() * total;
    let cumulative = 0;

    for(let i = 0; i < students.length; i++) {
        cumulative += students[i].probability;
        if(random <= cumulative) return i;
    }
    return students.length - 1;
}

function startSpin() {
    if(spinning) return;

    const winnerIndex = getWinnerIndex();
    const segmentAngle = 360 / students.reduce((sum, s) => sum + s.probability, 0) * students[winnerIndex].probability;
    const targetRotation = rotations * 360 + (360 - (winnerIndex * (360 / students.length) - segmentAngle/2));

    spinning = true;
    document.getElementById('result').textContent = '';

    const animate = () => {
        rotation += (targetRotation - rotation) * 0.02;
        canvas.style.transform = `rotate(${rotation}deg)`;

        if(Math.abs(targetRotation - rotation) < 0.1) {
            spinning = false;
            rotation = targetRotation % 360;
            document.getElementById('result').textContent =
                `🎉 Победитель: ${students[winnerIndex].name}! 🎉`;
        } else {
            requestAnimationFrame(animate);
        }
    };

    animate();
}

// Инициализация при загрузке
canvas.width = 400;
canvas.height = 400;
drawWheel();