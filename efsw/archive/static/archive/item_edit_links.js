define(['jquery', 'knockout', 'common/ajax_json_request', 'common/json_object_loader'], function($, ko, ajr, jol) {

    return function(conf, initial_data) {
        $(document).ready(function() {
            var view_model = new ItemEditLinksViewModel(conf.urls);
            view_model.init(initial_data);
            ko.applyBindings(view_model);
        });
    };

    function Item(data) {
        var default_values = { 'id': 0, 'name': '', 'url': '' };
        if (typeof data == 'undefined') {
            $.extend(true, this, default_values);
        } else {
            $.extend(true, this, default_values, data);
        }
    }

    function ItemEditLinksViewModel(urls) {
        var self = this;
        self.urls = urls;
        self.success_msg = ko.observable('');
        self.error_msg = ko.observable('');
        self.errors_empty = { 'type': '', 'item_select_type': '', 'item': '' };
        self.errors = ko.observable(self.errors_empty);
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

        self.add_item = function() {
            self.errors($.extend({}, self.errors_empty));
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

        };

        self._add_item_by_url = function() {

        };

        self.update_item = function() {

        };
    }

});