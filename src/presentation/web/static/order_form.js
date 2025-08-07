// /var/www/nexus-gear-store/src/static/order_form.js - ФИНАЛЬНАЯ ВЕРСИЯ

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

form.addEventListener('input', validateForm);

// Делаем обработчик асинхронным, чтобы использовать await
tg.onEvent('mainButtonClicked', async function () {
    mainButton.showProgress(false);
    mainButton.disable();

    const orderData = {
        full_name: nameInput.value,
        phone: phoneInput.value,
        address: addressInput.value,
        // ВАЖНО: Безопасно передаем данные о пользователе из Telegram
        user: tg.initDataUnsafe.user 
    };

    try {
        // Используем стандартный fetch для отправки данных на наш API
        const response = await fetch('/api/create_order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData),
        });

        if (!response.ok) {
            // Пытаемся получить текст ошибки от сервера
            const errorData = await response.json().catch(() => ({ message: 'Не удалось получить детали ошибки' }));
            throw new Error(errorData.message || `Ошибка сервера: ${response.status}`);
        }

        const result = await response.json();
        
        // Показываем пользователю сообщение об успехе и закрываем TWA
        tg.showAlert(`Ваш заказ №${result.order_id} успешно создан!`);
        tg.close();

    } catch (error) {
        // Показываем ошибку и возвращаем кнопку в активное состояние
        tg.showAlert(`Произошла ошибка: ${error.message}`);
        mainButton.hideProgress();
        mainButton.enable();
    }
});