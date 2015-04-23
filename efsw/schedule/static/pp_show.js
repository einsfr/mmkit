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
    var default_values = {
        id: 0,
        dow: '',
        start: '',
        end: '',
        comment: '',
        locked: false,
        program_id: 0,
        program_name: '',
        program_url: '',
        program_ls: '',
        program_age_limit: ''
    };
    if (typeof data == 'undefined') {
        $.extend(true, this, default_values);
    } else {
        $.extend(true, this, default_values, data);
    }
}

function LineupShowViewModel() {
    var self = this;

    self.pp_loaded = ko.observable(false);
    self.pp = ko.observable(new ProgramPosition());
    self._pp_cache = {};

    self._init_modal = function() {
        self.pp_loaded(false);
        self.pp(new ProgramPosition());
    };

    self.show_control_modal = function(pp_id) {
        self._init_modal();
        $('#pp_show_modal').modal();
        self._load_pp(pp_id);
    };

    self._load_pp = function(pp_id) {
        if (isNaN(pp_id)) {
            return;
        }
        if (pp_id.toString() in self._pp_cache) {
            self.pp($.extend(true, {}, self._pp_cache[pp_id.toString()]));
            self.pp_loaded(true);
            return;
        }
        $.getJSON(urls.pp_show_json(pp_id), function(response) {
            if (response.status == 'ok') {
                var pp = new ProgramPosition(response.data);
                self.pp(pp);
                // Если оставить просто знак равенства - содержимое кэша будет меняться при внесении изменений в форму
                self._pp_cache[pp_id.toString()] = $.extend(true, {}, pp);
                self.pp_loaded(true);
            } else {
                alert(response.data);
            }
        });
    };
}