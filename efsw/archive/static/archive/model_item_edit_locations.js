define(['jquery', 'knockout', 'common/ajax_json_request', 'common/json_object_loader'], function($, ko, ajr, jol) {

    function Location(data) {
        var default_values = { 'id': '', 'path': '', 'storage_id': '', 'storage_name': '' };
        if (typeof data == 'undefined') {
            $.extend(true, this, default_values);
        } else {
            $.extend(true, this, default_values, data);
        }
    }

    return function ItemEditLocationsViewModel(urls) {
        var self = this;
        self.urls = urls;
        self.error_msg = ko.observable('');
        self.locations_changed = ko.observable(false);
        self.errors = ko.observable({});
        self.locations = ko.observableArray([]);
        self.form_storage = ko.observable('');
        self.form_path = ko.observable('');

        $(window).bind('beforeunload', function() {
            if (self.locations_changed()) {
                return 'Обнаружены несохранённые изменения в размещении элемента в хранилищах - если сейчас покинуть страницу, они будут потеряны.';
            }
        });

        self.init = function(initial_data) {
            self.locations($.map(initial_data.locations, function(i) {
                return new Location(i);
            }));
        };

        self.remove_location = function(location) {
            self.locations.remove(location);
            self.locations_changed(true);
            self.error_msg('');
        };

        self.add_location = function() {
            var errors = {};
            if (!self.form_storage()) {
                errors.storage = 'Не выбрано хранилище.';
            }
            if (self.form_path() === undefined || self.form_path().length == 0) {
                errors.path = 'Не указан путь к файлу.';
            }
            self.errors(errors);
            if (errors.storage || errors.path) {
                return;
            }
            self.locations.push(new Location({
                'id': '',
                'path': self.form_path(),
                'storage_id': self.form_storage(),
                'storage_name': self._get_sel_storage_name()
            }));
            self.form_path('');
            self.locations_changed(true);
        };

        self.update_item = function() {
            ajr.exec(
                self.urls['item_update_locations_json'],
                {
                    'method': 'post',
                    'data':
                    {
                        'locations': ko.toJSON(self.locations().map(function(l) {
                            delete l.storage_name;
                            return l;
                        }))
                    }
                },
                function(response) {
                    self.locations_changed(false);
                    window.location.href = response.data;
                },
                function(response) {
                    self.error_msg(response.data);
                },
                alert
            );
        };

        self._get_sel_storage_name = function() {
            var elem = $('#id_storage').find('option[value=' + self.form_storage() + ']');
            return elem && elem.text();
        };

    }

});