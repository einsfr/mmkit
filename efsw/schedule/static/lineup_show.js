$(document).ready(function() {
    var view_model = new LineupShowViewModel()
    ko.applyBindings(view_model);
    var lineup_table = $("#lineup_table");
    lineup_table.disableSelection();
    lineup_table.on('dblclick', "tbody td", function() {
        view_model.process_dblclick();
    });
});

function LineupShowViewModel() {
    var self = this;

    self.process_dblclick = function() {
        alert('!!');
    };
}