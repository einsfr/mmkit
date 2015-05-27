define(['jquery', 'knockout', 'common/ajax_json_request'], function($, ko, ajr) {

    return function LineupCopyViewModel() {
        var self = this;

        self.form = $('#lineup_copy_form');
        self.errors = ko.observable({});
        self.non_field_errors = ko.observable('');

        self.init = function(urls, lineup_id) {
            self.urls = urls;
            self.lineup_id = lineup_id;
            self.errors({});
            self.non_field_errors('');
        };

        self.copy_lineup = function() {
            ajr.exec(
                self.urls.lineup_copy_json(self.lineup_id),
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
    };

});