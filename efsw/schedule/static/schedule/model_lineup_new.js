define(['jquery'], function($) {

    return function LineupNewViewModel(urls) {
        var self = this;
        self.urls = urls;

        self.create_lineup = function() {
            var form = $('#lineup_new_form');
            alert(form.serialize());
        };
    }

});