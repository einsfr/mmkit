define(['jquery', 'knockout', 'common/modal_loader', 'bootstrap'], function($, ko, ml) {

    return function(conf) {
        $(document).ready(function() {
            var view_model = new LineupListViewModel(conf.urls);
            ko.applyBindings(view_model);
            var icon_containers = $('table td.icon_actions_container');
            icon_containers.on('click', '.act_copy', function() {
                view_model.copy($(this).parents('tr').data('id'));
            });
            icon_containers.on('click', '.act_activate', function() {
                view_model.activate($(this).parents('tr').data('id'));
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
            ml.get_with_model(self.urls.lineup_copy_part_modal(), 'schedule/model_lineup_copy', function(modal_container, already_loaded, model) {
                model.init(urls, lineup_id);
                modal_container.modal();
            });
        };

        self.activate = function(lineup_id) {
            ml.get_with_model(self.urls.lineup_activate_part_modal(), 'schedule/model_lineup_activate', function(modal_container, already_loaded, model) {
                model.init(urls, lineup_id);
                modal_container.modal();
            })
        };

        self.make_draft = function(lineup_id) {
            ml.get_with_model(self.urls.lineup_make_draft_part_modal(), 'schedule/model_lineup_make_draft', function(modal_container, already_loaded, model) {
                model.init(urls, lineup_id);
                modal_container.modal();
            })
        };
    }

});