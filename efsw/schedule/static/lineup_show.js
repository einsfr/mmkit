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
        this.id = data.id;
        this.dow = data.dow;
        this.start_hours = data.start_hours;
        this.start_minutes = data.start_minutes;
        this.end_hours = data.end_hours;
        this.end_minutes = data.end_minutes;
        this.comment = data.comment;
        this.locked = data.locked;
        this.program_id = data.program_id;
    } else {
        this.id = 0;
        this.dow = '';
        this.start_hours = 0;
        this.start_minutes = 0;
        this.end_hours = 0;
        this.end_minutes = 0;
        this.comment = '';
        this.locked = false;
        this.program_id = 0;
    }
}

function Program(data) {
    if (data) {
        this.name = data.name;
        this.ls_hours = data.ls_hours;
        this.ls_minutes = data.ls_minutes;
        this.age_limit = data.age_limit;
    } else {
        this.name = '';
        this.ls_hours = 0;
        this.ls_minutes = 0;
        this.age_limit = ''
    }
}

function LineupShowViewModel() {
    var self = this;

    self.pp_loaded = ko.observable(false);
    self.pp = ko.observable(new ProgramPosition());
    self.program_loaded = ko.observable(false);
    self.program = ko.observable(new Program());
    self.modal_error = ko.observable('');
    self._pp_cache = {};
    self._program_cache = {};

    self.show_control_modal = function(pp_id) {
        self.pp(new ProgramPosition());
        self.pp_loaded(false);
        self.program_loaded(false);
        $('#pp_table_control_modal').modal();
        self._load_pp(pp_id);
    };

    self.program_changed = function() {
        if (self.pp().program_id) {
            self.program_loaded(false);
            self._load_program(self.pp().program_id);
        } else {
           self.program_loaded(true);
        }
    };

    self.pp_delete = function() {
        if (!confirm('Удалить фрагмент?')) {
            return;
        }
        $.ajax(urls.pp_delete_json(self.pp().id), { method: 'post' }).done(function(result) {
            if (result.status == 'ok') {
                alert('Удалено');
            } else {
                alert(result.data);
            }
        }).fail(function(jqXHR, textStatus) {
            alert('При удалении возникла ошибка: ' + textStatus);
        });
    };

    self._load_pp = function(pp_id) {
        if (isNaN(pp_id)) {
            return;
        }
        if (pp_id.toString() in self._pp_cache) {
            self.pp(self._pp_cache[pp_id.toString()]);
            self.pp_loaded(true);
            if (self.pp().program_id) {
                self._load_program(self.pp().program_id);
            } else {
                self.program(new Program());
                self.program_loaded(true);
            }
            return;
        }
        $.getJSON(urls.pp_show_json(pp_id), function(response) {
            if (response.status == 'ok') {
                var pp = new ProgramPosition(response.data);
                self.pp(pp);
                self._pp_cache[pp_id.toString()] = pp;
                self.pp_loaded(true);
                if (pp.program_id) {
                    self._load_program(pp.program_id);
                } else {
                    self.program(new Program());
                    self.program_loaded(true);
                }
            } else {
                alert(response.data);
            }
        });
    };

    self._load_program = function(program_id) {
        if (isNaN(program_id)) {
            return;
        }
        if (program_id.toString() in self._program_cache) {
            self.program(self._program_cache[program_id.toString()]);
            self.program_loaded(true);
            return;
        }
        $.getJSON(urls.program_show_json(program_id), function(response) {
            if (response.status == 'ok') {
                var program = new Program(response.data);
                self.program(program);
                self._program_cache[program_id.toString()] = program;
                self.program_loaded(true);
            } else {
                alert(response.data);
            }
        });
    };
}