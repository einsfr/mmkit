define(['jquery', 'knockout', 'jquery_ui', 'bootstrap'], function($, ko) {

    return function(conf) {

        $(document).ready(function() {
            var view_model = new LineupEditViewModel(conf.urls);
            ko.applyBindings(view_model);
            var lineup_table = $("#lineup_table");
            lineup_table.disableSelection();
            lineup_table.on('dblclick', "tbody td", function() {
                view_model.show_control_modal($(this).data('pp_id'));
            });
        });

    };

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
            this.similar_pps = data.similar_pps;
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
            this.similar_pps = [];
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

    function LineupEditViewModel(urls) {
        var self = this;

        self.pp_loaded = ko.observable(false);
        self.pp = ko.observable(new ProgramPosition());
        self.program_loaded = ko.observable(false);
        self.program = ko.observable(new Program());
        self._pp_cache = {};
        self._program_cache = {};
        self.urls = urls;

        self._init_modal = function() {
            self.pp_loaded(false);
            self.program_loaded(false);
            self.pp(new ProgramPosition());
            $('#repeat_select_container').find('input').attr('checked', false);
            $('#delete_confirm').collapse('hide');
        };

        self.show_control_modal = function(pp_id) {
            self._init_modal();
            $('#pp_edit_modal').modal();
            self._load_pp(pp_id);
        };

        self.program_changed = function() {
            if (self.pp().program_id) {
                self.program_loaded(false);
                self._load_program(self.pp().program_id);
            } else {
                self.program(new Program());
                self.program_loaded(true);
            }
        };

        self.pp_reload = function() {
            var pp_id = self.pp().id;
            self._init_modal();
            self._load_pp(pp_id);
        };

        self.pp_delete = function() {
            $.ajax(self.urls.pp_delete_json(self.pp().id), {
                method: 'post',
                data: $('#repeat_select_container').find('input').serialize()
            }).done(function(result) {
                self._process_change_result(result);
            }).fail(function(jqXHR, textStatus) {
                alert('При удалении возникла ошибка: ' + textStatus);
            });
        };

        self.pp_update = function() {
            $.ajax(self.urls.pp_update_json(self.pp().id), {
                method: 'post',
                data: $('#pp_form').serialize()
            }).done(function(result) {
                self._process_change_result(result);
            }).fail(function(jqXHR, textStatus) {
                alert('При обновлении возникла ошибка: ' + textStatus);
            });
        };

        self._process_change_result = function(result) {
            if (result.status == 'ok') {
                $('#pp_edit_modal').modal('hide');
            } else {
                alert(result.data);
            }
            self._pp_cache = [];
            $.ajax(self.urls.lineup_show_part_pp_table_body()).done(function(result) {
                $('#lineup_table').children('tbody').replaceWith('<tbody>' + result + '</tbody>');
            }).fail(function(jqXHR, textStatus) {
                alert('При обновлении таблицы возникла ошибка: ' + textStatus);
            });
        };

        self._load_pp = function(pp_id) {
            if (isNaN(pp_id)) {
                return;
            }
            if (pp_id.toString() in self._pp_cache) {
                self.pp($.extend(true, {}, self._pp_cache[pp_id.toString()]));
                self.pp_loaded(true);
                if (self.pp().program_id) {
                    self._load_program(self.pp().program_id);
                } else {
                    self.program(new Program());
                    self.program_loaded(true);
                }
                return;
            }
            $.getJSON(self.urls.pp_edit_json(pp_id), function(response) {
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

        self._load_program = function(program_id) {
            if (isNaN(program_id)) {
                return;
            }
            if (program_id.toString() in self._program_cache) {
                self.program(self._program_cache[program_id.toString()]);
                self.program_loaded(true);
                return;
            }
            $.getJSON(self.urls.program_show_json(program_id), function(response) {
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

});