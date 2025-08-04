// src/presentation/web/static/order_form.js - УПРОЩЕННАЯ ВЕРСИЯ

// Обертка DOMContentLoaded больше не нужна, так как скрипт подключен в конце body
const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();

const mainButton = tg.MainButton;
mainButton.setText('Отправить данные');
mainButton.disable();
mainButton.hide();

const form = document.getElementById('order-form');
const nameInput = document.getElementById('full_name');
const phoneInput = document.getElementById('phone');
const addressInput = document.getElementById('address');

function validateForm() {
    const isFormValid = nameInput.value.trim() !== '' &&
                        phoneInput.value.trim() !== '' &&
                        addressInput.value.trim() !== '';

    if (isFormValid) {
        mainButton.enable();
        mainButton.show();
    } else {
        mainButton.disable();
        mainButton.hide();
    }
}

// Этот код теперь гарантированно сработает, так как 'form' не будет null
form.addEventListener('input', validateForm);

tg.onEvent('mainButtonClicked', function () {
    // --- НАЧАЛО ФИНАЛЬНОГО ИСПРАВЛЕНИЯ ---

    // 1. Показываем индикатор загрузки, чтобы пользователь понял, что процесс пошел.
    tg.MainButton.showProgress(false); // false - круговой индикатор

    // 2. Делаем кнопку неактивной, чтобы избежать повторных нажатий.
    tg.MainButton.disable();

    // 3. Собираем данные.
    const data = {
        full_name: nameInput.value,
        phone: phoneInput.value,
        address: addressInput.value,
    };

    // 4. Отправляем данные.
    tg.sendData(JSON.stringify(data));
    
    // 5. Закрываем приложение.
    // Важно: tg.sendData асинхронна по своей природе, хотя и не возвращает Promise.
    // Telegram получает данные и сам решает, когда отправить сообщение.
    // Вызов tg.close() сразу после этого является стандартной практикой.
    tg.close();
    
    // --- КОНЕЦ ФИНАЛЬНОГО ИСПРАВЛЕНИЯ ---
});