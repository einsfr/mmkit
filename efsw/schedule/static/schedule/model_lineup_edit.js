define(['jquery', 'knockout'], function($, ko) {

    function ProgramPosition(data) {
        var default_values = {
            id: 0,
            dow: '',
            start_hours: 0,
            start_minutes: 0,
            end_hours: 0,
            end_minutes: 0,
            comment: '',
            locked: false,
            program_id: 0,
            similar_pps: []
        };
        if (typeof data == 'undefined') {
            $.extend(true, this, default_values);
        } else {
            $.extend(true, this, default_values, data);
        }
    }

    function Program(data) {
        var default_values = {
            name: '',
            ls_hours: 0,
            ls_minutes: 0,
            age_limit: ''
        };
        if (typeof data == 'undefined') {
            $.extend(true, this, default_values);
        } else {
            $.extend(true, this, default_values, data);
        }
    }

    return function LineupEditViewModel(urls, modal_container) {
        var self = this;

        self.pp_loaded = ko.observable(false);
        self.pp = ko.observable(new ProgramPosition());
        self.program_loaded = ko.observable(false);
        self.program = ko.observable(new Program());
        self._pp_cache = {};
        self._program_cache = {};
        self.urls = urls;
        self.modal_container = modal_container;

        self.init = function (pp_id) {
            self.pp_loaded(false);
            self.program_loaded(false);
            self.pp(new ProgramPosition());
            $('#repeat_select_container').find('input').attr('checked', false);
            $('#delete_confirm').collapse('hide');
            self._load_pp(pp_id);
        };

        self.program_changed = function () {
            if (self.pp().program_id) {
                self.program_loaded(false);
                self._load_program(self.pp().program_id);
            } else {
                self.program(new Program());
                self.program_loaded(true);
            }
        };

        self.pp_reload = function () {
            self.init(self.pp().id);
        };

        self.pp_delete = function () {
            $.ajax(self.urls.pp_delete_json(self.pp().id), {
                method: 'post',
                data: $('#repeat_select_container').find('input').serialize()
            }).done(function (result) {
                self._process_change_result(result);
            }).fail(function (jqXHR, textStatus) {
                alert('При удалении возникла ошибка: ' + textStatus);
            });
        };

        self.pp_update = function () {
            $.ajax(self.urls.pp_update_json(self.pp().id), {
                method: 'post',
                data: $('#pp_form').serialize()
            }).done(function (result) {
                self._process_change_result(result);
            }).fail(function (jqXHR, textStatus) {
                alert('При обновлении возникла ошибка: ' + textStatus);
            });
        };

        self._process_change_result = function (result) {
            if (result.status == 'ok') {
                self.modal_container.modal('hide');
            } else {
                alert(result.data);
            }
            self._pp_cache = [];
            $.ajax(self.urls.lineup_show_part_pp_table_body()).done(function (result) {
                $('#lineup_table').children('tbody').replaceWith('<tbody>' + result + '</tbody>');
            }).fail(function (jqXHR, textStatus) {
                alert('При обновлении таблицы возникла ошибка: ' + textStatus);
            });
        };

        self._load_pp = function (pp_id) {
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
            $.getJSON(self.urls.pp_edit_json(pp_id), function (response) {
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

        self._load_program = function (program_id) {
            if (isNaN(program_id)) {
                return;
            }
            if (program_id.toString() in self._program_cache) {
                self.program(self._program_cache[program_id.toString()]);
                self.program_loaded(true);
                return;
            }
            $.getJSON(self.urls.program_show_json(program_id), function (response) {
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