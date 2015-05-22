define(['jquery', 'knockout', 'common/ajax_json_request', 'jquery_ui', 'vendor/jquery-ui/i18n/datepicker-ru'], function($, ko, ajr) {

    return function(conf) {
        $(document).ready(function() {
            ko.applyBindings(new ItemNewViewModel(conf.urls));
            $('#id_created').datepicker(
                {
                    changeMonth: true,
                    changeYear: true,
                    yearRange: '1990:c',
                    maxDate: new Date()
                },
                $.datepicker.regional['ru']
            );
        });
    };

    function ItemNewViewModel(urls) {
        var self = this;
        self.urls = urls;
        self.form = $('#item_new_form');
        self.errors_empty = { 'name': '', 'description': '', 'created': '', 'author': '', 'category': '' };
        self.errors = ko.observable(self.errors_empty);
        self.non_field_errors = ko.observable('');

        self.create_item = function() {
            ajr.exec(
                self.urls.item_create_json(),
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
    }

});