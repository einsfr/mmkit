define(['jquery', 'knockout', 'common/ajax_json_request', 'common/json_object_loader'], function($, ko, ajr, jol) {

    return function ItemEditLocationsViewModel(urls) {
        var self = this;
        self.urls = urls;
        self.error_msg = ko.observable('');
        self.locations_changed = ko.observable(false);
        self.errors = ko.observable({});

        $(window).bind('beforeunload', function() {
            if (self.locations_changed()) {
                return 'Обнаружены несохранённые изменения в размещении элемента в хранилищах - если сейчас покинуть страницу, они будут потеряны.';
            }
        });

        self.init = function(initial_data) {

        };

        self.update_item = function() {

        };

    }

});