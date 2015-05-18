define(['jquery', 'knockout'], function($, ko) {

    return function LineupMakeDraftViewModel() {
        var self = this;

        self.non_field_errors = ko.observable('');

        self.init = function(urls, lineup_id) {
            self.urls = urls;
            self.lineup_id = lineup_id;
            self.non_field_errors('');
        };

        self.lineup_make_draft = function() {
            $.ajax(self.urls.lineup_make_draft_json(self.lineup_id), {
                'method': 'post'
            }).done(function(response) {
                if (response.status == 'ok') {
                    window.location.reload();
                } else {
                    self.non_field_errors(response.data);
                }
            }).fail(function(jqXHR, textStatus, errorThrown) {
                self.non_field_errors('При возврате к черновику возникла ошибка: ' + errorThrown);
            });
        };
    };

});