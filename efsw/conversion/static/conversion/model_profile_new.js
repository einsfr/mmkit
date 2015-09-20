define(['jquery', 'knockout', 'common/ajax_json_request'], function($, ko, ajr) {

    function IOViewModel(data) {
        var default_values = { 'position': 0, 'io_type': '' };
        if (typeof data == 'undefined') {
            $.extend(true, this, default_values);
        } else {
            $.extend(true, this, default_values, data);
        }
        this.errors = ko.observable({});
    }

    return function ProfileNewViewModel(urls) {
        var self = this;
        self.urls = urls;
        self.errors = ko.observable({});
        self.error_msg = ko.observable('');

        self.profile_form = $('#profile_new_form');
        self.profile_form.submit(function() {
            return false;
        });

        self.inputs = ko.observableArray([]);
        var total_inputs = parseInt($('#id_inputs-TOTAL_FORMS').val());
        for (var i = 0; i < total_inputs; i++) {
            self.inputs.push(new IOViewModel({ 'position': i, 'io_type': 'i' }));
        }

        self.outputs = ko.observableArray([]);
        var total_outputs = parseInt($('#id_outputs-TOTAL_FORMS').val());
        for (var o = 0; o < total_outputs; o++) {
            self.outputs.push(new IOViewModel({ 'position': o, 'io_type': 'o' }));
        }

        self.submit_form = function() {

        };
    };

});
