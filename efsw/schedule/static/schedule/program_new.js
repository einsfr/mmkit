define(['jquery', 'knockout'], function($, ko) {

    return function(conf) {
        $(document).ready(function() {
            ko.applyBindings(new ProgramNewViewModel(conf.urls));
        })
    };

    function ProgramNewViewModel(urls) {
        var self = this;

        self.urls = urls;
        self.form = $('#program_new_form');
        self.errors_empty = {
            'name': '',
            'description': '',
            'age_limit': '',
            'lineup_size': '',
            'max_duration': '',
            'min_duration': ''
        };
        self.errors = ko.observable(self.errors_empty);
        self.non_field_errors = ko.observable('');

        self.create_program = function() {
            $.ajax(self.urls.program_create_json(), {
                'method': 'post',
                'data': self.form.serialize()
            }).done(function(response) {
                if (response.status == 'ok') {
                    window.location.href = response.data;
                } else {
                    require(['common/form_error_parser'], function(parser) {
                        parser.parse(response.data, self.errors, self.non_field_errors);
                    });
                }
            }).fail(function(jqXHR, textStatus, errorThrown) {
                self.non_field_errors('При создании программы возникла ошибка: ' + errorThrown);
            });
        };
    }

});