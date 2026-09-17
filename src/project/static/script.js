$(document).ready(function(){
    $('#67').on('submit',function(e){
        e.preventDefault();
        err = 0;
        if (err == 0){
            $.ajax({
                url: '/user_register',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    name: $('#fullname').val(),
                    password: $('#password').val(),
                    email: $('#email').val()
                })
            })
        }
    })


   $('#lg').on('submit',function(e){
        e.preventDefault();
        err = 0;
        if (err == 0){
            $.ajax({
                url: '/user_login',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    uname: $('#username').val(),
                    password: $('#password').val()
                })
            })
        }
    })

})