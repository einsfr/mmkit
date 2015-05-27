define(['jquery', 'knockout', 'common/ajax_json_request', 'common/json_object_loader'], function($, ko, ajr, jol) {

    return function(conf, initial_data) {
        $(document).ready(function() {
            var view_model = new ItemEditLocationsViewModel(conf.urls);
            view_model.init(initial_data);
            ko.applyBindings(view_model);
        });
    };

    function ItemLocation(data) {
        var default_values = { 'id': 0, 'storage_id': 0, 'storage_name': '', 'location': '', 'base_url': '' };
        if (typeof data == 'undefined') {
            $.extend(true, this, default_values);
        } else {
            $.extend(true, this, default_values, data);
        }
    }

    function ItemStorage(data) {
        var default_values = {'id': 0, 'name': '', 'base_url': '', 'disable_location': false };
        if (typeof data == 'undefined') {
            $.extend(true, this, default_values);
        } else {
            $.extend(true, this, default_values, data);
        }
    }

    function ItemEditLocationsViewModel(urls) {
        var self = this;
        self.urls = urls;
        self.success_msg = ko.observable('');
        self.error_msg = ko.observable('');
        self.errors_empty = { 'storage': '', 'location': '' };
        self.locations = ko.observableArray([]);
        self.locations_changed = ko.observable(false);
        self.errors = ko.observable(self.errors_empty);
        self.form_storage = ko.observable();
        self.form_location = ko.observable('');

        $(window).bind('beforeunload', function() {
            if (self.locations_changed()) {
                return 'Обнаружены несохранённые изменения в размещении элемента в хранилищах - если сейчас покинуть страницу, они будут потеряны.';
            }
        });

        self.init = function(initial_data) {
            self.locations($.map(initial_data.locations, function(l) {
                return new ItemLocation(l);
            }));
            self.form_storage(new ItemStorage(initial_data.storage));
        };

        self.remove_location = function(location) {
            self.locations.remove(location);
            self.locations_changed(true);
            self.success_msg('');
            self.error_msg('');
        };

        self.add_location = function() {
            var errors = $.extend({}, self.errors_empty);
            if (!self.form_storage().id || isNaN(self.form_storage().id)) {
                errors.storage = 'Не выбрано хранилище.';
            }
            if (!self.form_storage().disable_location && (self.form_location() === undefined || self.form_location().length == 0)) {
                errors.location = 'Не указано положение в хранилище.';
            }
            self.errors(errors);
            if (errors.storage || errors.location) {
                return;
            }
            self.locations.push(new ItemLocation({
                id: 0,
                storage_name: self.form_storage().name,
                storage_id: self.form_storage().id,
                base_url: self.form_storage().base_url,
                location: self.form_storage().disable_location ? '<<будет определено автоматически>>' : self.form_location()
            }));
            self.locations_changed(true);
            self.success_msg('');
        };

        self.update_item = function() {
            ajr.exec(
                self.urls.item_update_locations_json(),
                {
                    'method': 'post',
                    'data':
                    {
                        'locations': ko.toJSON(self.locations().map(function(l) {
                            delete l.storage_name;
                            delete l.base_url;
                            return l;
                        }))
                    }
                },
                function() {
                    self.error_msg('');
                    self.success_msg('Изменения сохранены.');
                    self.locations_changed(false);
                    ajr.exec(
                        self.urls.item_show_locations_json(),
                        function(response) {
                            self.locations($.map(response.data, function(data) {
                                return new ItemLocation(data);
                            }));
                        },
                        alert,
                        alert
                    );
                },
                function(response) {
                    self.success_msg('');
                    self.error_msg(response.data);
                },
                alert
            );
        };

        self.storage_changed = function() {
            var id = self.form_storage().id;
            if (!id || isNaN(id)) {
                return;
            }
            self.form_location('');
            jol.load(
                self.urls.storage_show_json(id),
                {},
                ItemStorage,
                self.form_storage,
                alert,
                alert
            );
        };
    }

});