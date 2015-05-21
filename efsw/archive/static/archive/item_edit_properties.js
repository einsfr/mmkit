define(['jquery', 'knockout', 'common/ajax_json_request', 'jquery_ui', 'vendor/jquery-ui/i18n/datepicker-ru'], function($, ko, ajr) {

    return function(conf) {
        $(document).ready(function() {
            ko.applyBindings(new ItemEditPropertiesViewModel(conf.urls));
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

    function ItemEditPropertiesViewModel(urls) {
        var self = this;
        self.urls = urls;
        self.form = $('#item_edit_form');
        self.errors_empty = { 'name': '', 'description': '', 'created': '', 'author': '', 'category': '' };
        self.errors = ko.observable(self.errors_empty);
        self.non_field_errors = ko.observable('');
        self.success_msg = ko.observable('');

        self.update_item = function() {
            ajr.exec(
                self.urls.item_update_properties_json(),
                { 'method': 'post', 'data': self.form.serialize() },
                function() {
                    self.success_msg('Изменения сохранены.');
                },
                function(response) {
                    self.success_msg('');
                    require(['common/form_error_parser'], function(parser) {
                        parser.parse(response.data, self.errors, self.non_field_errors);
                    });
                },
                alert
            );
        };
    }

});