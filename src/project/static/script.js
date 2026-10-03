$(document).ready(function(){
    $('#67').on('submit',function(e){
        e.preventDefault();
        $.ajax({
            url: '/user_register',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                name: $('#fullname').val(),
                password: $('#password').val(),
                email: $('#email').val()
            }),
            success: function(response) {
                if(response.result) {
                    window.location.href = '/lk'; // Перенаправление при успехе
                } else {
                    alert('Ошибка регистрации! Возможно, Email уже занят.');
                }
            }
        });
    });

   $('#lg').on('submit',function(e){
        e.preventDefault();
        $.ajax({
            url: '/user_login',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                uname: $('#username').val(),
                p_hash: $('#password').val() 
            }),
            success: function(response) {
                if(response.result) {
                    window.location.href = '/lk'; // Перенаправление при успехе
                } else {
                    alert('Неверный логин или пароль!');
                }
            }
        });
    });

    // Обработка кнопки "Пополнить баланс"
    $('#topup-btn').on('click', function() {
        alert('Функция пополнения временно недоступна (заглушка).');
    });

    // Обработка кнопки "Сделать запрос"
    $('#make-request-btn').on('click', function() {
        $.ajax({
            url: '/make_request',
            method: 'POST',
            success: function(response) {
                if(response.result) {
                    // Визуально обновляем баланс без перезагрузки страницы
                    $('.balance-value').html(response.new_balance + '<span class="currency">₽</span>');
                    alert('Запрос успешно выполнен! С баланса списано 3 ₽.');
                } else {
                    alert('Ошибка: ' + response.error);
                }
            }
        });
    });
});