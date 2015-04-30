define(['jquery', 'common/modal_loader'], function($, ml) {

    return function(conf) {
        $(document).ready(function() {
            $('#lineup_new_modal_switch').on('click', function () {
                ml(conf.urls.lineup_new_part_modal(), function(modal) {
                    if (modal) {
                        modal.modal();
                    }
                });
            });
        });
    }

});