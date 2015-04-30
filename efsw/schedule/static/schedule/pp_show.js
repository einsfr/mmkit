define(['jquery', 'knockout', 'schedule/lineup_show_view_model', 'bootstrap'], function($, ko, model) {

    return function(conf) {

        $(document).ready(function() {
            var view_model = new model(conf.urls);
            ko.applyBindings(view_model);
            var lineup_table = $("#lineup_table");
            lineup_table.disableSelection();
            lineup_table.on('dblclick', "tbody td", function() {
                view_model.show_control_modal($(this).data('pp_id'));
            });
        });

    };

});