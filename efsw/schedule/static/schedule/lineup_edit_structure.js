define(['jquery', 'knockout', 'common/modal_loader', 'jquery_ui', 'bootstrap'], function($, ko, ml) {

    var view_model;

    return function(conf) {

        $(document).ready(function() {
            var lineup_table = $("#lineup_table");
            lineup_table.disableSelection();
            lineup_table.on('dblclick', "tbody td", function() {
                var pp_id = $(this).data('pp_id');
                ml(conf.urls.pp_edit_part_modal(), function(modal_container, already_loaded) {
                    if (modal_container) {
                        if (typeof view_model == 'undefined') {
                            require(['schedule/model_lineup_edit'], function(model) {
                                view_model = new model(conf.urls, modal_container);
                                ko.applyBindings(view_model, modal_container.children()[0]);
                                view_model.init(pp_id);
                                modal_container.modal();
                            });
                        } else {
                            if (!already_loaded) {
                                ko.applyBindings(view_model, modal_container.children()[0]);
                            }
                            view_model.init(pp_id);
                            modal_container.modal();
                        }
                    }
                });
            });
        });

    };

});