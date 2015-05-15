define(['knockout'], function(ko) {

    function Lineup(data) {

    }

    return function LineupCopyViewModel() {
        var self = this;

        self.lineup_loaded = ko.observable(false);
        self.lineup = ko.observable(new Lineup());

        self.init = function(urls, lineup_id) {
            self.urls = urls;
            self.lineup_loaded(false);
            self.lineup(new Lineup());
            self._load_lineup(lineup_id);
        };

        self._load_lineup = function(lineup_id) {
            if (isNaN(lineup_id)) {
                return;
            }

            self.lineup_loaded(true);
        };
    };

});