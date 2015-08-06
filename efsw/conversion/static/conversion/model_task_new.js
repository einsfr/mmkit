define(['jquery', 'knockout'], function($, ko) {

    function InputOutput(data) {
        var default_values = { 'comment': '' };
        if (typeof data == 'undefined') {
            $.extend(true, this, default_values);
        } else {
            $.extend(true, this, default_values, data);
        }
    }

    return function TaskNewViewModel(urls) {
        var self = this;
        self.urls = urls;
        self.errors = ko.observable({});
        self.inputs = ko.observableArray([
            new InputOutput({ 'comment': '' }),
            new InputOutput({ 'comment': 'Комментарий ко входу 1' }),
            new InputOutput({ 'comment': '' })
        ]);
        self.outputs = ko.observableArray([
            new InputOutput({ 'comment': 'Комментарий к выходу 0' }),
            new InputOutput({ 'comment': '' })
        ]);
    };

});
