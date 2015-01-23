$(document).ready(function() {

    $("#item-links-container").find("a[id^='item-remove-link-']").click(function(event) {
        event.preventDefault();
        if (false === confirm('Удалить связь?')) {
            return;
        }
        var url = this.href;
        $.get(url, function(data, status) {
            if (status == 'success') {
                $('#item-remove-link-' + data).parent().remove();
            } else {
                alert('Ошибка удаления связи');
            }
        });
    });

});