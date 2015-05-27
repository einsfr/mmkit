define(['jquery', 'knockout', 'common/ajax_json_request', 'jquery_ui', 'vendor/jquery-ui/i18n/datepicker-ru'], function($, ko, ajr) {

    // http://stackoverflow.com/questions/21059598/implementing-jquery-datepicker-in-bootstrap-modal
    $.fn.modal.Constructor.prototype.enforceFocus = function() {};

    return function LineupActivateViewModel() {
        var self = this;

        self.form = $('#lineup_activate_form');
        self.errors = ko.observable({});
        self.non_field_errors = ko.observable('');

        self.init = function(urls, lineup_id) {
            self.urls = urls;
            self.lineup_id = lineup_id;
            self.errors({});
            self.non_field_errors('');
            self.form.find('#id_active_since').datepicker(
                {
                    changeMonth: true,
                    changeYear: true,
                    minDate: '+1d'
                },
                $.datepicker.regional['ru']
            );
        };

        self.activate_lineup = function() {
            ajr.exec(
                self.urls.lineup_activate_json(self.lineup_id),
                { 'method': 'post', 'data': self.form.serialize() },
                function() {
                    window.location.reload();
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