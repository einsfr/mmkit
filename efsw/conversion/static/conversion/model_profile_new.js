define(['jquery', 'knockout', 'common/json_object_loader', 'common/ajax_json_request'], function($, ko, jol, ajr) {

    return function ProfileNewViewModel(urls) {
        var self = this;
        self.urls = urls;
        self.errors = ko.observable({});
        self.error_msg = ko.observable('');
        self.profile_form = $('#profile_new_form');

        self.profile_form.submit(function() {
            return false;
        });

        self.submit_form = function() {

        };
    };

});
