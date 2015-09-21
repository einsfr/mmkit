define(['jquery', 'knockout', 'common/ajax_json_request'], function($, ko, ajr) {

    function IOViewModel(data) {
        if (typeof data == 'undefined') {
            this.position = ko.observable(0);
            this.io_type = '';
        } else {
            this.position = ko.observable(data.position);
            this.io_type = data.io_type;
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
        self.total_inputs = parseInt($('#id_inputs-TOTAL_FORMS').val());
        for (var i = 0; i < self.total_inputs; i++) {
            self.inputs.push(new IOViewModel({ 'position': i, 'io_type': 'i' }));
        }

        self.outputs = ko.observableArray([]);
        self.total_outputs = parseInt($('#id_outputs-TOTAL_FORMS').val());
        for (var o = 0; o < self.total_outputs; o++) {
            self.outputs.push(new IOViewModel({ 'position': o, 'io_type': 'o' }));
        }

        self._clear_errors = function() {
            self.errors({});
            self.error_msg('');
            var clear_errors = function(e) {
                e.errors({});
                return e;
            };
            self.inputs($.map(self.inputs(), clear_errors));
            self.outputs($.map(self.outputs(), clear_errors));
        };

        self._set_input_errors = function(errors) {
            var inputs = self.inputs();
            for (var i = 0; i < inputs.length; i++) {
                inputs[i].errors(errors[i]);
            }
            self.inputs(inputs);
        };

        self._set_output_errors = function(errors) {
            var outputs = self.outputs();
            for (var i = 0; i < outputs.length; i++) {
                outputs[i].errors(errors[i]);
            }
            self.outputs(outputs);
        };

        self._append_error_msg = function (msg) {
            self.error_msg(self.error_msg() + ' ' + msg);
        };

        self.submit_form = function() {
            self._clear_errors();
            ajr.exec(
                self.urls['profile_create_json'],
                { 'method': 'post', 'data': self.profile_form.serialize() },
                function(response) {
                    window.location.href = response.data;
                },
                function(response) {
                    require(['common/form_error_parser'], function(parser) {
                        parser.parse(response.data, self.errors, self.error_msg, alert);
                        parser.parse_formset(
                            response.data, 'inputs', self._set_input_errors, self._append_error_msg, alert
                        );
                        parser.parse_formset(
                            response.data, 'outputs', self._set_output_errors, self._append_error_msg, alert
                        );
                    });
                },
                alert
            )
        };

        self.add_input = function() {
            self.inputs.push(new IOViewModel({ 'position': self.inputs().length, 'io_type': 'i' }));
            self.total_inputs++;
            $('#id_inputs-TOTAL_FORMS').val(self.total_inputs);
        };

        self.add_output = function() {
            self.outputs.push(new IOViewModel({ 'position': self.outputs().length, 'io_type': 'o' }));
            self.total_outputs++;
            $('#id_outputs-TOTAL_FORMS').val(self.total_outputs);
        };

        self.remove_io = function(data) {
            var target_array_observable;
            if (data.io_type == 'i') {
                target_array_observable = self.inputs;
                self.total_inputs--;
                $('#id_inputs-TOTAL_FORMS').val(self.total_inputs);
            } else {
                target_array_observable = self.outputs;
                self.total_outputs--;
                $('#id_outputs-TOTAL_FORMS').val(self.total_outputs);
            }
            target_array_observable.remove(data);
            var removed_pos = data.position();
            target_array_observable().forEach(function(io) {
                if (io.position() > removed_pos) {
                    io.position(io.position() - 1);
                }
            });
        };
    };

});
