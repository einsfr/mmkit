define(['jquery', 'knockout', 'common/ajax_json_request'], function ($, ko, ajr) {

    return function (conf) {
        $(document).ready(function () {
            ko.applyBindings(new CategoryEditViewModel(conf.urls));
        });
    };

    function CategoryEditViewModel(urls) {
        var self = this;

        self.urls = urls;
        self.form = $('#category_update_form');
        self.errors = ko.observable({});
        self.error_msg = ko.observable('');

        self.category_update = function () {
            self.error_msg('');
            ajr.exec(
                self.urls.category_update_json(),
                {'method': 'post', 'data': self.form.serialize()},
                function (response) {
                    window.location.href = response.data;
                },
                function (response) {
                    require(['common/form_error_parser'], function (parser) {
                        parser.parse(response.data, self.errors, self.error_msg, alert);
                    });
                },
                alert
            );
        };
    }

});