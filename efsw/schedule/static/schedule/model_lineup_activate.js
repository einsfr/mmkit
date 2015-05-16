define(['jquery', 'knockout', 'jquery_ui', 'vendor/jquery-ui/i18n/datepicker-ru'], function($, ko) {

    return function LineupActivateViewModel() {
        var self = this;

        self.form = $('#lineup_activate_form');
        self.errors_empty = {
            name: ''
        };
        self.errors = ko.observable(self.errors_empty);
        self.non_field_errors = ko.observable('');

        self.init = function(urls, lineup_id) {
            self.urls = urls;
            self.lineup_id = lineup_id;
            self.errors(self.errors_empty);
            self.non_field_errors('');
            self.form.find('#id_active_since').datepicker(
                {
                    changeMonth: true,
                    changeYear: true,
                    minDate: '+1d'
                },
                $.datepicker.regional['ru']
            );
        };

        self.activate_lineup = function() {
            $.ajax(self.urls.lineup_activate_json(self.lineup_id), {
                'method': 'post',
                'data': self.form.serialize()
            }).done(function(response) {
                if (response.status == 'ok') {

                } else {
                    require(['common/form_error_parser'], function(parser) {
                        parser.parse(response.data, self.errors, self.non_field_errors);
                    });
                }
            }).fail(function(jqXHR, textStatus, errorThrown) {
                self.non_field_errors('При активации возникла ошибка: ' + errorThrown);
            });
        };
    };

});