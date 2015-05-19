define(['jquery', 'knockout', 'tinycolor'], function($, ko, tc) {

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
            'min_duration': '',
            'color': ''
        };
        self.errors = ko.observable(self.errors_empty);
        self.non_field_errors = ko.observable('');
        self.color_input = $('#id_color');
        self.selected_color = ko.observable(self.color_input.val());

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

        self.change_color = function() {
            var new_color = tc.random();
            while (new_color.toHsl().l < 0.7) {
                new_color.lighten();
            }
            while (new_color.toHsl().s > 0.5) {
                new_color.desaturate();
            }
            self.color_input.val(new_color.toHexString());
            self.color_changed();
        };

        self.color_changed = function() {
            var new_color = tc(self.color_input.val());
            if (!new_color.isValid()) {
                return;
            }
            var new_color_hex_string = new_color.toHexString();
            if (new_color.getFormat() != 'hex') {
                self.color_input.val(new_color_hex_string);
            }
            self.selected_color(new_color_hex_string);
        }
    }

});