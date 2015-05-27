define(['jquery', 'knockout', 'common/ajax_json_request'], function($, ko, ajr) {

    return function GenericFormModel(form_selector, submit_url, ok_callback, options) {
        var self = this;

        self.form = $(form_selector);
        self.submit_url = submit_url;
        if (typeof ok_callback == 'undefined') {
            self.ok_callback = function() {};
        } else {
            self.ok_callback = ok_callback;
        }
        var default_options = {
            'success_msg': 'Изменения сохранены.'
        };
        if (typeof options == 'undefined') {
            self.options = default_options;
        } else {
            self.options = $.extend(true, default_options, options);
        }

        self.errors = ko.observable({});
        self.error_msg = ko.observable('');
        self.success_msg = ko.observable('');

        // http://stackoverflow.com/questions/11235622/jquery-disable-form-submit-on-enter
        self.form.on('keyup keypress', function(e) {
            var code = e.keyCode || e.which;
            if (code == 13) {
                e.preventDefault();
                self.submit_form();
                return false;
            }
        });

        self.submit_form = function() {
            self.error_msg('');
            self.success_msg('');
            self.errors({});
            ajr.exec(
                self.submit_url,
                { 'method': 'post', 'data': self.form.serialize() },
                function(response) {
                    self.success_msg(self.options.success_msg);
                    self.ok_callback(response);
                },
                function(response) {
                    require(['common/form_error_parser'], function(parser) {
                        parser.parse(response.data, self.errors, self.error_msg, alert);
                    });
                },
                alert
            );
        }

    };

});