define(['jquery', 'knockout', 'common/ajax_json_request'], function($, ko, ajr) {

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
            ajr.exec(
                self.urls.lineup_update_json(),
                { method: 'post', data: self.form.serialize() },
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
    }

});