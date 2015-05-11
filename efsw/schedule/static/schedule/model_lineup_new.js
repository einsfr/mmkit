define(['jquery', 'knockout'], function($, ko) {

    return function LineupNewViewModel(urls) {
        var self = this;
        self.urls = urls;
        self.form = $('#lineup_new_form');
        self.errors_empty = {
            name: '',
            start_time: '',
            end_time: '',
            channel: ''
        };
        self.errors = ko.observable(self.errors_empty);

        self.init = function() {
            self.errors(self.errors_empty);
        };

        self.create_lineup = function() {
            $.ajax(self.urls.lineup_create_json(), {
                method: 'post',
                data: self.form.serialize()
            }).done(function(result) {
                if (result.status == 'ok') {
                    window.location.href = result.data;
                } else {
                    var errors = $.parseJSON(result.data.errors);
                    for (var p in errors) {
                        if (errors.hasOwnProperty(p)) {
                            errors[p] = errors[p].map(function(e) { return e.message; }).join(' ');
                        }
                    }
                    self.errors(errors);
                }
            }).fail(function(jqXHR, textStatus) {
                alert('При создании возникла ошибка: ' + textStatus);
            });
        };
    }

});