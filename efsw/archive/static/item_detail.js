$(document).ready(function() {

    $("#item-links-container").on('click', "a[id^='item-remove-link-']", function(event) {
        event.preventDefault();
        if (false === confirm('Удалить связь?')) {
            return;
        }
        var form = $(this).parent();
        var url = form.attr('action');
        $.ajax({
            type: 'POST',
            url: url,
            data: form.serialize(),
            statusCode: {
                200: function(data) {
                    $('#item-remove-link-' + data).closest('li').remove();
                },
                400: function(data) {
                    alert('Ошибка удаления связи');
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
                    alert('Ошибка добавления связи');
                }
            }
        });
    });


    $("#item-add-storage-form").on('submit', function(event) {
        event.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        $.ajax({
            type: 'POST',
            url: url,
            data: form.serialize(),
            statusCode: {
                200: function(data) {
                    $('#item-add-storage-form').before(data);
                },
                400: function() {
                    alert('Ошибка добавления элемента в хранилище');
                }
            }
        });
    });

    ko.applyBindings(new IncludesListViewModel());
});

function Item(data) {
    this.name = ko.observable(data.name);
    this.url = ko.observable(data.url);
    this.url_title = ko.observable(data.url_title);
}

function IncludesListViewModel() {
    var self = this;
    self.includes = ko.observableArray([]);

    var json_url = $("#includes_container").data('url');
    $.getJSON(json_url, function(includes_data) {
        var mapped_includes = $.map(includes_data, function(item) {
            return new Item(item);
        });
        self.includes(mapped_includes);
    });
}