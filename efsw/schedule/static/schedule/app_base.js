$(document).ready(function() {
    var lineup_new_view_model = new LineupNewViewModel()
    ko.applyBindings(lineup_new_view_model, document.getElementById('lineup_new_modal'));
    $('#lineup_new_modal_switch').on('click', function() {
        lineup_new_view_model.show_modal();
    });
});

function LineupNewViewModel() {
    var self = this;

    self.show_modal = function() {
        $('#lineup_new_modal').modal();
    };
}