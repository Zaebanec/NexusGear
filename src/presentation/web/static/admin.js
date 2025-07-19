document.addEventListener('DOMContentLoaded', function () {
    // Инициализируем объект Telegram Web App
    let tg = window.Telegram.WebApp;

    // Сообщаем Telegram, что приложение готово к отображению
    tg.ready();
    
    // Расширяем приложение на всю высоту
    tg.expand();

    const addProductForm = document.getElementById('add-product-form');

    // Функция-заглушка для загрузки товаров
    function loadProducts() {
        console.log('Загрузка списка товаров...');
        // TODO: Реализовать fetch-запрос к API бэкенда для получения списка товаров
        // Пример:
        // fetch('/api/v1/products')
        //     .then(response => response.json())
        //     .then(products => {
        //         const productList = document.getElementById('product-list');
        //         productList.innerHTML = ''; // Очищаем список
        //         products.forEach(product => {
        //             const productDiv = document.createElement('div');
        //             productDiv.innerText = `${product.name} - ${product.price} руб.`;
        //             productList.appendChild(productDiv);
        //         });
        //     });
    }

    // Функция-заглушка для добавления нового товара
    function addProduct(event) {
        event.preventDefault(); // Предотвращаем стандартную отправку формы
        console.log('Добавление нового товара...');

        const formData = new FormData(addProductForm);
        const productData = Object.fromEntries(formData.entries());

        console.log('Данные для отправки:', productData);

        // TODO: Реализовать fetch-запрос к API бэкенда для добавления товара
        // Пример:
        // fetch('/api/v1/products', {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json',
        //     },
        //     body: JSON.stringify(productData),
        // })
        // .then(response => response.json())
        // .then(newProduct => {
        //     console.log('Товар добавлен:', newProduct);
        //     loadProducts(); // Обновляем список товаров
        //     addProductForm.reset(); // Очищаем форму
        //     tg.showAlert('Товар успешно добавлен!');
        // });
    }

    // Назначаем обработчик на отправку формы
    addProductForm.addEventListener('submit', addProduct);

    // Загружаем товары при старте
    loadProducts();
});