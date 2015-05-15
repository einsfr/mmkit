define(['jquery', 'knockout', 'common/json_object_loader'], function($, ko, obj_loader) {

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

    return function LineupEditViewModel() {
        var self = this;

        self.pp_loaded = ko.observable(false);
        self.pp = ko.observable(new ProgramPosition());
        self.program_loaded = ko.observable(false);
        self.program = ko.observable(new Program());

        self.init = function (urls, modal_container, pp_id) {
            self.urls = urls;
            self.modal_container = modal_container;
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
            obj_loader.load(
                self.urls.pp_edit_json(pp_id),
                ProgramPosition,
                function(o) {
                    self.pp(o);
                    self.pp_loaded(true);
                }
            );
        };

        self._load_program = function (program_id) {
            if (isNaN(program_id)) {
                return;
            }
            obj_loader.load(
                self.urls.program_show_json(program_id),
                Program,
                function(o) {
                    self.program(o);
                    self.program_loaded(true);
                }
            );
        };
    }

});