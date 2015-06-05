define(['jquery', 'knockout', 'common/ajax_json_request'], function($, ko, ajr) {

    return function ChannelListViewModel(urls) {
        var self = this;

        self.urls = urls;
        self.error_msg = ko.observable('');

        self.activate = function(channel_id) {
            ajr.exec(
                self.urls.channel_activate_json(channel_id),
                { 'method': 'post' },
                function() {
                    window.location.reload();
                },
                function(response) {
                    self.error_msg(response.data);
                },
                alert
            );
        };

        self.deactivate = function(channel_id) {
            ajr.exec(
                self.urls.channel_deactivate_json(channel_id),
                { 'method': 'post' },
                function() {
                    window.location.reload();
                },
                function(response) {
                    self.error_msg(response.data);
                },
                alert
            );
        };

    }

});