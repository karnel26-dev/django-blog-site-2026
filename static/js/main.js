// Функция 1: подсветка карточки поста при двойном клике.
// Это простой пример работы с событиями и CSS-классами.
document.addEventListener('dblclick', function (event) {
    const card = event.target.closest('.post-card');

    if (card) {
        card.classList.toggle('highlight');
    }
});

// Функция 2: подтверждение перед отправкой формы удаления.
// Находим кнопку с классом danger внутри формы и спрашиваем пользователя.
document.addEventListener('submit', function (event) {
    const dangerButton = event.target.querySelector('button.danger');

    if (dangerButton && !confirm('Точно выполнить это действие?')) {
        event.preventDefault();
    }
});
