define(['jquery', 'knockout', 'common/ajax_json_request', 'common/json_object_loader'], function($, ko, ajr, jol) {

    function Item(data) {
        var default_values = { 'id': 0, 'name': '', 'url': '' };
        if (typeof data == 'undefined') {
            $.extend(true, this, default_values);
        } else {
            $.extend(true, this, default_values, data);
        }
    }

    return function ItemEditLinksViewModel(urls) {
        var self = this;
        self.urls = urls;
        self.success_msg = ko.observable('');
        self.error_msg = ko.observable('');
        self.errors = ko.observable({});
        self.includes_changed = ko.observable(false);
        self.includes = ko.observableArray([]);
        self.included_in = ko.observableArray([]);
        self.form_type = ko.observable(1);
        self.form_item_select_type = ko.observable(1);
        self.form_item = ko.observable('');

        $(window).bind('beforeunload', function() {
            if (self.includes_changed()) {
                return 'Обнаружены несохранённые изменения в связанных элементах - если сейчас покинуть страницу, они будут потеряны.';
            }
        });

        self.init = function(initial_data) {
            self.includes($.map(initial_data.includes, function(i) {
                return new Item(i);
            }));
            self.included_in($.map(initial_data.included_in, function(i) {
                return new Item(i);
            }));
        };

        self._set_error = function(name, text) {
            var errors = self.errors();
            errors[name] = text;
            self.errors(errors);
        };

        self.remove_includes = function(inc) {
            self.success_msg('');
            self.error_msg('');
            self.includes_changed(true);
            self.includes.remove(inc);
        };

        self.remove_included_in = function(inc) {
            self.success_msg('');
            self.error_msg('');
            self.includes_changed(true);
            self.included_in.remove(inc);
        };

        self.add_item = function() {
            self.errors({});
            self.success_msg('');
            self.error_msg('');
            if (self.form_type() != '1' || self.form_type() != '2') {
                self._set_error('type', 'Неизвестный тип связи.');
            }
            if (self.form_item_select_type() == '1') {
                self._add_item_by_id();
            } else if (self.form_item_select_type() == '2') {
                self._add_item_by_url();
            } else {
                self._set_error('item_select_type', 'Неизвестный тип выбора элемента.');
            }
        };

        self._add_item_by_id = function() {
            if (isNaN(self.form_item())) {
                self._set_error('item', 'При выборе элемента по ID, ID должен быть целым числом.');
                return;
            }
            var _equal_id = function(i) {
                return (i.id == self.form_item());
            };
            if (self.includes().some(_equal_id) || self.included_in().some(_equal_id)) {
                self._set_error('item', 'Связь с элементом с таким ID уже существует.');
                return;
            }
            jol.load(
                self.urls['item_check_links_json'],
                {
                    'data': {
                        'include_id': self.form_item(),
                        'type': self.form_type()
                    }
                },
                Item,
                function(i) {
                    if (self.form_type() == '1') {
                        self.included_in.push(i);
                    } else if (self.form_type() == '2') {
                        self.includes.push(i);
                    }
                    self.includes_changed(true);
                },
                function(e) {
                    self.error_msg(e.data);
                },
                alert
            )
        };

        self._add_item_by_url = function() {
            // TODO: Написать реализацию
        };

        self.update_item = function() {
            ajr.exec(
                self.urls['item_update_links_json'],
                {
                    'data': {
                        'includes': ko.toJSON(
                            self.includes().map(function(i) {
                                return i.id;
                            })
                        ),
                        'included_in': ko.toJSON(
                            self.included_in().map(function(i) {
                                return i.id;
                            })
                        )
                    },
                    'method': 'post'
                },
                function() {
                    self.error_msg('');
                    self.success_msg('Изменения сохранены.');
                    self.includes_changed(false);
                },
                function(response) {
                    self.success_msg('');
                    self.error_msg(response.data);
                },
                alert
            );
        };
    }

});