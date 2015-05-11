define(['jquery', 'knockout', 'schedule/model_lineup_new'], function($, ko, model) {

    return function(conf) {
        $(document).ready(function() {
            ko.applyBindings(new model(conf.urls));
        })
    }

});