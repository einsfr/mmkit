$(document).ready(function() {
    ko.applyBindings(new ItemDetailViewModel());
});

function Item(data) {
    this.id = ko.observable(data.id);
    this.name = ko.observable(data.name);
    this.url = ko.observable(data.url);
    this.url_title = ko.observable(data.url_title);
}

function ItemDetailViewModel() {
    var self = this;
    self.includes = ko.observableArray([]);
    self.included_item_id = ko.observable();
    var json_url = $("#includes_container").data('url');

    self.remove_include = function(item) {
        self.includes.remove(item);
    };

    self.add_include = function() {
        if (isNaN(self.included_item_id())) {
            return;
        }
        if (self.includes().some(function(i) {
                return (i.id() == self.included_item_id());
            })) {
            alert('Элемент уже включён в список');
            return;
        }
        $.getJSON(json_url + self.included_item_id() + '/', function(response) {
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
        var update_url = form.attr('action');
        var csrf_token = form.children("input[name='csrfmiddlewaretoken']").val();
        $.ajax(update_url, {
            data: {
                csrfmiddlewaretoken: csrf_token,
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

    $.getJSON(json_url, function(response) {
        if (response.status == 'ok') {
            var mapped_includes = $.map(response.data, function(item) {
                return new Item(item);
            });
            self.includes(mapped_includes);
        } else {
            alert(response.data);
        }
    });
}