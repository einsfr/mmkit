define(['jquery', 'knockout', 'common/json_object_loader'], function($, ko, obj_loader) {

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

    return function LineupShowViewModel() {
        var self = this;

        self.pp_loaded = ko.observable(false);
        self.pp = ko.observable(new ProgramPosition());

        self.init = function(urls, pp_id) {
            self.urls = urls;
            self.pp_loaded(false);
            self.pp(new ProgramPosition());
            self._load_pp(pp_id);
        };

        self._load_pp = function(pp_id) {
            if (isNaN(pp_id)) {
                return;
            }
            obj_loader.load(
                self.urls.pp_show_json(pp_id),
                {},
                ProgramPosition,
                function(o) {
                    self.pp(o);
                    self.pp_loaded(true);
                },
                function(response) {
                    alert(response.data);
                },
                alert
            );
        };
    }

});