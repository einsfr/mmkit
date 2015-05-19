define(['jquery', 'knockout', 'common/ajax_json_request'], function($, ko, ajr) {

    return function LineupMakeDraftViewModel() {
        var self = this;

        self.non_field_errors = ko.observable('');

        self.init = function(urls, lineup_id) {
            self.urls = urls;
            self.lineup_id = lineup_id;
            self.non_field_errors('');
        };

        self.lineup_make_draft = function() {
            ajr.exec(
                self.urls.lineup_make_draft_json(self.lineup_id),
                { 'method': 'post' },
                function() {
                    window.location.reload();
                },
                self.non_field_errors,
                alert
            );
        };
    };

});