define(['jquery', 'knockout'], function($, ko) {

    return function(conf) {
        $(document).ready(function() {
            ko.applyBindings(new LineupUpdateViewModel(conf.urls));
        })
    };

    function LineupUpdateViewModel(urls) {
        var self = this;
        self.urls = urls;
        self.form = $('#lineup_update_form');
        self.errors_empty = {
            name: ''
        };
        self.errors = ko.observable(self.errors_empty);
        self.non_field_errors = ko.observable('');

        self.init = function() {
            self.errors(self.errors_empty);
        };

        self.update_lineup = function() {

            $.ajax(self.urls.lineup_update_json(), {
                method: 'post',
                data: self.form.serialize()
            }).done(function(result) {
                if (result.status == 'ok') {
                    window.location.href = result.data;
                } else {
                    require(['common/form_error_parser'], function(parser) {
                        parser.parse(result.data, self.errors, self.non_field_errors);
                    });
                }
            }).fail(function(jqXHR, textStatus) {
                alert('При обновлении возникла ошибка: ' + textStatus);
            });
        };
    }

});