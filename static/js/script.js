function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ready(function() {
    console.log("JS файл успешно подключен и готов к работе!");

    $('.vote-btn').click(function(e) {
        e.preventDefault();
        
        let $btn = $(this);
        let $widget = $btn.closest('.vote-widget');
        let itemId = $btn.data('id');
        let itemType = $btn.data('type');
        let action = $btn.data('action');
        
        $widget.find('.vote-btn').prop('disabled', true);
        
        let url = itemType === 'question' ? '/ajax/like-question/' : '/ajax/like-answer/';
        
        $.ajax({
            url: url,
            type: 'POST',
            data: {
                [itemType + '_id']: itemId,
                'action': action
            },
            success: function(response) {
                $('#rating-' + itemType + '-' + itemId).text(response.rating);
                
                if ($btn.hasClass('active')) {
                    $btn.removeClass('active');
                } else {
                    $widget.find('.vote-btn').removeClass('active');
                    $btn.addClass('active');
                }
            },
            error: function(xhr) {
                if (xhr.status === 401) {
                    alert('Пожалуйста, авторизуйтесь для голосования.');
                    window.location.href = '/login/';
                } else {
                    let errorMsg = xhr.responseJSON ? xhr.responseJSON.error : 'Произошла ошибка';
                    alert('Ошибка: ' + errorMsg);
                }
            },
            complete: function() {
                $widget.find('.vote-btn').prop('disabled', false);
            }
        });
    });

    $('.correct-checkbox').change(function(e) {
        let $checkbox = $(this);
        let answerId = $checkbox.data('id');
        
        $checkbox.prop('disabled', true);
        
        $.ajax({
            url: '/ajax/mark-correct/',
            type: 'POST',
            data: { 'answer_id': answerId },
            success: function(response) {
                $checkbox.prop('checked', response.is_correct);
            },
            error: function(xhr) {
                $checkbox.prop('checked', !$checkbox.prop('checked'));
                
                if (xhr.status === 401) {
                    alert('Необходимо авторизоваться.');
                    window.location.href = '/login/';
                } else if (xhr.status === 403) {
                    alert('Ошибка доступа: Только автор вопроса может выбирать правильный ответ.');
                } else {
                    alert('Произошла непредвиденная ошибка.');
                }
            },
            complete: function() {
                $checkbox.prop('disabled', false);
            }
        });
    });
});