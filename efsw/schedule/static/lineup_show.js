$(document).ready(function() {
    var view_model = new LineupShowViewModel()
    ko.applyBindings(view_model);
    var lineup_table = $("#lineup_table");
    lineup_table.disableSelection();
    lineup_table.on('dblclick', "tbody td", function() {
        view_model.show_control_modal($(this).data('pp_id'));
    });
});

function LineupShowViewModel() {
    var self = this;

    self.pp_loaded = ko.observable(false);
    self.pp_cache = [];

    self.show_control_modal = function(pp_id) {
        self.pp_loaded(false);
        $('#pp_table_control_modal').modal();
    };
}