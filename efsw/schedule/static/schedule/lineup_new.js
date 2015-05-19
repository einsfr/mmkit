define(['jquery', 'knockout', 'common/ajax_json_request'], function($, ko, ajr) {

    return function(conf) {
        $(document).ready(function() {
            ko.applyBindings(new LineupNewViewModel(conf.urls));
        })
    };

    function LineupNewViewModel(urls) {
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
            ajr.exec(
                self.urls.lineup_create_json(),
                { method: 'post', data: self.form.serialize() },
                function(response) {
                    window.location.href = response.data;
                },
                function(response) {
                    require(['common/form_error_parser'], function(parser) {
                        parser.parse(response.data, self.errors);
                    });
                },
                alert
            );
        };
    }

});