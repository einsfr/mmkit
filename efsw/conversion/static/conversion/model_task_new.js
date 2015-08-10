define(['jquery', 'knockout', 'common/json_object_loader', 'common/ajax_json_request'], function($, ko, jol, ajr) {

    function InputOutput(data) {
        var default_values = { 'position': 0, 'comment': '' };
        if (typeof data == 'undefined') {
            $.extend(true, this, default_values);
        } else {
            $.extend(true, this, default_values, data);
        }
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

        self.replace_prefix = function(elements, item) {
            var position = item.position;
            elements.forEach(function(e) {
                if (e.nodeType == 1) {
                    e.innerHTML = e.innerHTML.replace(/__prefix__/g, position);
                }
            });
        };

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
                    f.setAttribute('value', self.inputs().length);
                }
            });
        };

        self.profile_changed = function(data, event) {
            self.errors({});
            self.error_msg('');
            var profile_id = event.currentTarget.value;
            if (profile_id) {
                jol.load(
                    self.urls.profile_show_json(),
                    {
                        'data': {
                            'id': profile_id
                        }
                    },
                    Profile,
                    function(profile) {
                        self.profile_description(profile.description);
                        self.inputs($.map(profile.inputs, function(data) {
                            return new InputOutput(data);
                        }));
                        self._set_inputs_mf_values();
                        self.outputs($.map(profile.outputs, function(data) {
                            return new InputOutput(data);
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

        self.submit_form = function() {
            self.error_msg('');
            self.errors({});
            ajr.exec(
                self.urls.task_create_json(),
                { 'method': 'post', 'data': self.task_form.serialize() },
                function(response) {
                    // ok
                },
                function(response) {
                    require(['common/form_error_parser'], function(parser) {
                        parser.parse(response.data, self.errors, self.error_msg, alert);
                    });
                },
                alert
            );
        };
    };

});
