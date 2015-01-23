$(document).ready(function() {

    $("#item-links-container").find("a[id^='item-remove-link-']").click(function(event) {
        event.preventDefault();
        if (false === confirm('Удалить связь?')) {
            return;
        }
        var url = this.href;
        $.ajax({
            type: 'GET',
            url: url,
            statusCode: {
                200: function(data) {
                    $('#item-remove-link-' + data).parent().remove();
                }
            }
        });
    });

    $("#item-add-link-form").on('submit', function(event) {
        event.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        $.ajax({
            type: 'POST',
            url: url,
            data: form.serialize(),
            statusCode: {
                200: function(data) {
                    $('#item-links-container').find('li:last-child').before(data);
                },
                400: function() {
                    alert('Ошибка добавления связи')
                }
            }
        });
    });

});