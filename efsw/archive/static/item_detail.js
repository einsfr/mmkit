$(document).ready(function() {
    ko.applyBindings(new ItemDetailViewModel());
});

function Item(data) {
    this.id = data.id;
    this.name = data.name;
    this.url = data.url;
}

function ItemLocation(data) {
    this.id = data.id;
    this.storage_id = data.storage_id;
    this.storage = data.storage;
    this.location = data.location;
}

function ItemStorage(data) {
    if (data) {
        this.id = data.id,
        this.name = data.name,
        this.base_url = data.base_url,
        this.disable_location = data.disable_location
    } else {
        this.id = 0,
        this.name = '',
        this.base_url = '',
        this.disable_location = false
    }
}

function ItemDetailViewModel() {
    var self = this;
    self.includes = ko.observableArray([]);
    self.include_item_id = ko.observable();
    self.locations = ko.observableArray([]);
    self.location = ko.observable();
    self.storage_id = ko.observable();
    self.selected_storage = ko.observable(new ItemStorage());
    self.locations_changed = false;

    self.remove_include = function(item) {
        self.includes.remove(item);
    };

    self.add_include = function() {
        if (isNaN(self.include_item_id())) {
            alert('Идентификатор должен быть числом');
            return;
        }
        if (self.includes().some(function(i) {
                return (i.id == self.include_item_id());
            })) {
            alert('Элемент уже включён в список');
            return;
        }
        $.getJSON(urls.item_includes_get(), {id: self.include_item_id()}, function(response) {
            if (response.status == 'ok') {
                self.includes.push(new Item(response.data));
            } else {
                alert(response.data);
            }
        });
    };

    self.update_includes = function() {
        $.ajax(
            $("#includes_update_form").data('update-url'),
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
                } else {
                    alert(result.data);
                }
            }
        ).fail(function(jqXHR, textStatus) {
                alert('При сохранении возникла ошибка: ' + textStatus);
            }
        );
    };

    self.remove_location = function(location) {
        self.locations.remove(location);
        self.locations_changed = true;
    };

    self.add_location = function() {
        if (!self.storage_id() || isNaN(self.storage_id())) {
            alert('Не выбрано хранилище');
            return;
        }
        if (!self.selected_storage().disable_location && (self.location() === undefined || self.location().length == 0)) {
            alert('Не указано положение в хранилище');
            return;
        }
        self.locations.push(new ItemLocation({
            id: 0,
            storage: self.selected_storage().name,
            storage_id: self.selected_storage().id,
            location: self.selected_storage().disable_location ? 'Определяется автоматически' : self.location()
        }));
        self.locations_changed = true;
    };

    self.update_locations = function() {
        if (false === self.locations_changed) {
            alert('Изменений не обнаружено');
            return;
        }
        $.ajax(
            $("#locations_update_form").data('update-url'),
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

    self.storage_changed = function() {
        if (self.storage_id() && !isNaN(self.storage_id())) {
            $.getJSON(urls.storages_get(), { id: self.storage_id() }, function(response) {
                if (response.status == 'ok') {
                    self.selected_storage(new ItemStorage(response.data));
                } else {
                    alert(response.data);
                }
            });
        }
    };

    self._get_locations = function() {
        $.getJSON(urls.item_locations_list_json(), function(response) {
            if (response.status == 'ok') {
                var mapped_locations = $.map(response.data, function(location) {
                    return new ItemLocation(location);
                });
                self.locations(mapped_locations);
            } else {
                alert(response.data);
            }
        });
    };

    self._get_includes = function() {
        $.getJSON(urls.item_includes_list_json(), function(response) {
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

    self._get_locations();
    self._get_includes();
}