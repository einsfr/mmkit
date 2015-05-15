define(['jquery', 'knockout'], function($, ko) {

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
            $.ajax(self.urls.lineup_create_json(), {
                method: 'post',
                data: self.form.serialize()
            }).done(function(result) {
                if (result.status == 'ok') {
                    window.location.href = result.data;
                } else {
                    require(['common/form_error_parser'], function(parser) {
                        parser.parse(result.data, self.errors);
                    });
                }
            }).fail(function(jqXHR, textStatus) {
                alert('При создании возникла ошибка: ' + textStatus);
            });
        };
    }

});