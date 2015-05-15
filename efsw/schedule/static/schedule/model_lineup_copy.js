define(['jquery', 'knockout'], function($, ko) {

    function Lineup(data) {

    }

    return function LineupCopyViewModel() {
        var self = this;

        self.form = $('#lineup_copy_form');
        self.errors_empty = {
            name: ''
        };
        self.errors = ko.observable(self.errors_empty);
        self.non_field_errors = ko.observable('');

        self.init = function(urls, lineup_id) {
            self.urls = urls;
            self.lineup_id = lineup_id;
            self.errors(self.errors_empty);
        };

        self.copy_lineup = function() {
            $.ajax(self.urls.lineup_copy_json(self.lineup_id), {
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
                self.non_field_errors('При копировании возникла ошибка: (' + textStatus + ') - ' + errorThrown);
            });
        };
    };

});