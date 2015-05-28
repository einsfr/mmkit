define(['common/modal_loader'], function(ml) {

    return function LineupListViewModel(urls) {
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