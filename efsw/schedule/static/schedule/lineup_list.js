define(['jquery', 'knockout', 'common/modal_loader', 'bootstrap'], function($, ko, ml) {

    return function(conf) {
        $(document).ready(function() {
            var view_model = new LineupListViewModel(conf.urls);
            ko.applyBindings(view_model);
            var icon_containers = $('table td.icon_actions_container');
            icon_containers.on('click', '.act_copy', function() {
                view_model.copy($(this).parents('tr').data('id'));
            });
            icon_containers.on('click', '.act_make_not_draft', function() {
                view_model.make_not_draft($(this).parents('tr').data('id'));
            });
            icon_containers.on('click', '.act_make_draft', function() {
                view_model.make_draft($(this).parents('tr').data('id'));
            });
        });
    };

    function LineupListViewModel(urls) {
        var self = this;

        self.urls = urls;

        self.copy = function(lineup_id) {
            ml(self.urls.lineup_copy_part_modal(), function(modal_container, already_loaded) {
                if (modal_container) {
                    if (typeof self.copy_model == 'undefined') {
                        require(['schedule/model_lineup_copy'], function(model) {
                            self.copy_model = new model(self.urls);
                            ko.applyBindings(self.copy_model, modal_container.children()[0]);
                            modal_container.modal();
                        });
                    } else {
                        if (!already_loaded) {
                            ko.applyBindings(self.copy_model, modal_container.children()[0]);
                        }
                        modal_container.modal();
                    }
                }
            });
        };

        self.make_not_draft = function(lineup_id) {

        };

        self.make_draft = function(lineup_id) {

        };
    }

});