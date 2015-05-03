define(['jquery', 'knockout'], function($, ko) {

    return function LineupNewViewModel(urls, modal_container) {
        var self = this;
        self.urls = urls;
        self.modal_container = modal_container;
        self.form = $('#lineup_new_form');
        self.errors = ko.observable({});

        self.init = function() {
            self.errors({});
        };

        self.create_lineup = function() {
            $.ajax(self.urls.lineup_create(), {
                method: 'post',
                data: self.form.serialize()
            }).done(function(result) {
                if (result.status == 'ok') {
                    alert('ok');
                } else {
                    self.errors($.parseJSON(result.data.errors));
                }
            }).fail(function(jqXHR, textStatus) {
                alert('При создании возникла ошибка: ' + textStatus);
            });
        };
    }

});