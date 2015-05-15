define(['jquery', 'knockout', 'common/modal_loader', 'jquery_ui', 'bootstrap'], function($, ko, ml) {

    return function(conf) {
        $(document).ready(function() {
            var lineup_table = $("#lineup_table");
            lineup_table.disableSelection();
            lineup_table.on('dblclick', "tbody td", function() {
                var pp_id = $(this).data('pp_id');
                ml.get_with_model(conf.urls.pp_show_part_modal(), 'schedule/model_lineup_show', function(modal_container, already_loaded, model) {
                    model.init(conf.urls, pp_id);
                    modal_container.modal();
                });
            });
        });
    };

});