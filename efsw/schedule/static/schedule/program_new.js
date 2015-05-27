define(['jquery', 'knockout', 'tinycolor', 'common/ajax_json_request'], function($, ko, tc, ajr) {

    return function(conf) {
        $(document).ready(function() {
            ko.applyBindings(new ProgramNewViewModel(conf.urls));
        })
    };

    function ProgramNewViewModel(urls) {
        var self = this;

        self.urls = urls;
        self.form = $('#program_new_form');
        self.errors = ko.observable({});
        self.non_field_errors = ko.observable('');
        self.color_input = $('#id_color');
        self.selected_color = ko.observable(self.color_input.val());

        self.create_program = function() {
            ajr.exec(
                self.urls.program_create_json(),
                { 'method': 'post', 'data': self.form.serialize() },
                function(response) {
                    window.location.href = response.data;
                },
                function(response) {
                    require(['common/form_error_parser'], function(parser) {
                        parser.parse(response.data, self.errors, self.non_field_errors, alert);
                    });
                },
                alert
            );
        };

        self.change_color = function() {
            var new_color = tc.random();
            while (new_color.toHsl().l < 0.75) {
                new_color.lighten();
            }
            while (new_color.toHsl().s > 0.75) {
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