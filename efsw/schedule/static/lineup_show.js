$(document).ready(function() {
    var view_model = new LineupShowViewModel();
    ko.applyBindings(view_model);
    var lineup_table = $("#lineup_table");
    lineup_table.disableSelection();
    lineup_table.on('dblclick', "tbody td", function() {
        view_model.show_control_modal($(this).data('pp_id'));
    });
});

function ProgramPosition(data) {
    if (data) {
        this.start_hours = data.start_hours;
        this.start_minutes = data.start_minutes;
        this.end_hours = data.end_hours;
        this.end_minutes = data.end_minutes;
        this.comment = data.comment;
        this.locked = data.locked;
    } else {
        this.start_hours = 0;
        this.start_minutes = 0;
        this.end_hours = 0;
        this.end_minutes = 0;
        this.comment = '';
        this.locked = false;
    }
}

function LineupShowViewModel() {
    var self = this;

    self.pp_loaded = ko.observable(false);
    self.pp = ko.observable(new ProgramPosition());
    self._pp_cache = [];
    self._program_cache = [];

    self.show_control_modal = function(pp_id) {
        self.pp(new ProgramPosition());
        self.pp_loaded(false);
        $('#pp_table_control_modal').modal();
        self._load_pp(pp_id)
    };

    self._load_pp = function(pp_id) {
        // сначала надо проверить на предмет нахожденния в кэше
        $.getJSON(urls.pp_show_json(pp_id), function(response) {
            if (response.status == 'ok') {
                self.pp(new ProgramPosition(response.data));
                self.pp_loaded = true;
                // и ещё нужно закэшировать
            } else {
                alert(response.data);
            }
        });
    }
}