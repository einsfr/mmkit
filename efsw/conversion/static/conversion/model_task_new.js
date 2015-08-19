define(['jquery', 'knockout', 'common/json_object_loader', 'common/ajax_json_request'], function($, ko, jol, ajr) {

    function InputOutputViewModel(data) {
        var default_values = { 'position': 0, 'comment': '', 'io_type': '', 'allowed_ext': [] };
        if (typeof data == 'undefined') {
            $.extend(true, this, default_values);
        } else {
            $.extend(true, this, default_values, data);
        }
        this.errors = ko.observable({});
        this.allowed_ext = (this.allowed_ext.length ? $.map(this.allowed_ext, function(e) {
            return '*.' + e;
        }) : ['*.*']);
    }

    function Profile(data) {
        var default_values = { 'name': '', 'description': '', 'inputs': [], 'outputs': [] };
        if (typeof data == 'undefined') {
            $.extend(true, this, default_values);
        } else {
            $.extend(true, this, default_values, data);
        }
    }

    return function TaskNewViewModel(urls) {
        var self = this;
        self.urls = urls;
        self.errors = ko.observable({});
        self.error_msg = ko.observable('');
        self.profile_description = ko.observable('');
        self.inputs = ko.observableArray([]);
        self.outputs = ko.observableArray([]);
        self.task_form = $('#task_new_form');

        self.task_form.submit(function() {
            return false;
        });

        self._set_inputs_mf_values = function() {
            var inputs_mf_fields = $('#inputs_management_form_container').find('input').toArray();
            var inputs_fields_names = [
                'inputs-TOTAL_FORMS', 'inputs-INITIAL_FORMS', 'inputs-MIN_NUM_FORMS', 'inputs-MAX_NUM_FORMS'
            ];
            inputs_mf_fields.forEach(function(f) {
                if (inputs_fields_names.indexOf(f.getAttribute('name')) >= 0) {
                    f.setAttribute('value', self.inputs().length);
                }
            });
        };

        self._set_outputs_mf_values = function() {
            var outputs_mf_fields = $('#outputs_management_form_container').find('input').toArray();
            var outputs_fields_names = [
                'outputs-TOTAL_FORMS', 'outputs-INITIAL_FORMS', 'outputs-MIN_NUM_FORMS',
                'outputs-MAX_NUM_FORMS'
            ];
            outputs_mf_fields.forEach(function(f) {
                if (outputs_fields_names.indexOf(f.getAttribute('name')) >= 0) {
                    f.setAttribute('value', self.outputs().length);
                }
            });
        };

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

        self.profile_changed = function(data, event) {
            self._clear_errors();
            var profile_id = event.currentTarget.value;
            if (profile_id) {
                jol.load(
                    self.urls['profile_show_json'],
                    {
                        'data': {
                            'id': profile_id
                        }
                    },
                    Profile,
                    function(profile) {
                        self.profile_description(profile.description);
                        self.inputs($.map(profile.inputs, function(data) {
                            data.io_type = 'i';
                            return new InputOutputViewModel(data);
                        }));
                        self._set_inputs_mf_values();
                        self.outputs($.map(profile.outputs, function(data) {
                            data.io_type = 'o';
                            return new InputOutputViewModel(data);
                        }));
                        self._set_outputs_mf_values();
                    },
                    function(e) {
                        alert(e.data);
                    },
                    alert
                );
            } else {
                self.profile_description('');
                self.inputs([]);
                self._set_inputs_mf_values();
                self.outputs([]);
                self._set_outputs_mf_values();
            }
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
                self.urls['task_create_json'],
                { 'method': 'post', 'data': self.task_form.serialize() },
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
            );
        };
    };

});
