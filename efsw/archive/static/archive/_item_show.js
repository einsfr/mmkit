define(['jquery', 'knockout', 'bootstrap'], function($, ko) {

    return function(conf) {
        $(document).ready(function() {
            var view_model = new ItemDetailViewModel(conf.urls);
            ko.applyBindings(view_model);
            view_model.storage_changed();
        });
    };

    function ItemDetailViewModel(urls) {
        var self = this;
        self.includes = ko.observableArray([]);
        self.include_item_id = ko.observable();
        self.locations = ko.observableArray([]);
        self.location = ko.observable();
        self.storage_id = ko.observable();
        self.selected_storage = ko.observable(new ItemStorage());
        self.locations_changed = false;
        self.includes_changed = false;
        self.urls = urls;

        self.remove_include = function(item) {
            self.includes.remove(item);
            self.includes_changed = true;
        };

        self.add_include = function() {
            if (isNaN(self.include_item_id())) {
                alert('Идентификатор должен быть целым числом');
                return;
            }
            if (self.includes().some(function(i) {
                    return (i.id == self.include_item_id());
                })) {
                alert('Элемент уже включён в список');
                return;
            }
            $.getJSON(self.urls.item_includes_check_json(), {include_id: self.include_item_id()}, function(response) {
                if (response.status == 'ok') {
                    self.includes.push(new Item(response.data));
                    self.includes_changed = true;
                } else {
                    alert(response.data);
                }
            });
        };

        self.update_includes = function() {
            $.ajax(
                self.urls.item_includes_update_json(),
                {
                    data: {
                        includes: ko.toJSON(
                            self.includes().map(function(i) {
                                return i.id;
                            })
                        )
                    },
                    method: 'post'
                }
            ).done(function(result) {
                    if (result.status == 'ok') {
                        alert('Сохранено');
                        self.includes_changed = false;
                    } else {
                        alert(result.data);
                    }
                }
            ).fail(function(jqXHR, textStatus) {
                    alert('При сохранении возникла ошибка: ' + textStatus);
                }
            );
        };

        self.update_locations = function() {
            if (false === self.locations_changed) {
                alert('Изменений не обнаружено');
                return;
            }
            $.ajax(
                self.urls.item_locations_update_json(),
                {
                    data: {
                        locations: ko.toJSON(
                            self.locations().map(function(i) {
                                delete i.storage;
                                return i;
                            })
                        )
                    },
                    method: 'post'
                }
            ).done(function(result) {
                    if (result.status == 'ok') {
                        alert('Сохранено');
                        self._get_locations();
                        self.locations_changed = false;
                    } else {
                        alert(result.data);
                    }
                }
            ).fail(function(jqXHR, textStatus) {
                    alert('При сохранении возникла ошибка: ' + textStatus);
                }
            );
        };

        self._get_includes = function() {
            $.getJSON(self.urls.item_includes_list_json(), function(response) {
                if (response.status == 'ok') {
                    var mapped_includes = $.map(response.data, function(item) {
                        return new Item(item);
                    });
                    self.includes(mapped_includes);
                } else {
                    alert(response.data);
                }
            });
        };

        self._get_includes();
    }

});