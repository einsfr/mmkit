$(document).ready(function() {
    ko.applyBindings(new ItemDetailViewModel());
});

function Item(data) {
    this.id = data.id;
    this.name = data.name;
    this.url = data.url;
    this.url_title = data.url_title;
}

function ItemLocation(data) {
    this.id = data.id;
    this.storage = data.storage;
    this.location = data.location;
}

function Storage(data) {
    if (data) {
        this.id = data.id,
        this.name = data.name,
        this.type = data.type,
        this.base_url = data.base_url,
        this.description = data.description,
        this.mount_dir = data.mount_dir
    } else {
        this.id = 0,
        this.name = '',
        this.type = '',
        this.base_url = '',
        this.description = '',
        this.mount_dir = ''
    }
}

function ItemDetailViewModel() {
    var self = this;
    self.includes = ko.observableArray([]);
    self.include_item_id = ko.observable();
    self.locations = ko.observableArray([]);
    self.location = ko.observable();
    self.storage_id = ko.observable();
    self.selected_storage = ko.observable(new Storage());

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
                return;
            }
        });
    };

    self.update_includes = function() {
        var form = $("#includes_update_form");
        $.ajax(
            form.attr('action'),
            {
                data: {
                    csrfmiddlewaretoken: form.children("input[name='csrfmiddlewaretoken']").val(),
                    data: ko.toJSON({
                        includes: self.includes().map(function(i) {
                            return i.id;
                        })
                    })
                },
                type: 'post',
                success: function(result) {
                    if (result.status == 'ok') {
                        alert('Сохранено');
                    } else {
                        alert(result.data);
                        return;
                    }
                }
            });
    };

    self.remove_location = function(location) {
        self.locations.remove(location);
    };

    self.add_location = function() {
        if (!self.storage_id() || isNaN(self.storage_id())) {
            alert('Не выбрано хранилище');
            return;
        }
        if (self.location() === undefined || self.location().length == 0) {
            alert('Неправильное положение в хранилище');
            return;
        }
    };

    self.update_locations = function() {

    };

    self.storage_changed = function() {
        if (self.storage_id() && isNaN(self.storage_id())) {
            $.getJSON();
        }
    };

    $.getJSON(urls.item_includes_get(), function(response) {
        if (response.status == 'ok') {
            var mapped_includes = $.map(response.data, function(item) {
                return new Item(item);
            });
            self.includes(mapped_includes);
        } else {
            alert(response.data);
        }
    });

    $.getJSON(urls.item_locations_get(), function(response) {
        if (response.status == 'ok') {
            var mapped_locations = $.map(response.data, function(location) {
                return new ItemLocation(location);
            });
            self.locations(mapped_locations);
        } else {
            alert(response.data);
        }
    });
}