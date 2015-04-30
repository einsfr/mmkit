define(['jquery', 'jquery_ui', 'vendor/jquery-ui/i18n/datepicker-ru'], function($) {

    return function() {

        $(document).ready(function() {
            $('#created_date_input').datepicker(
                {
                    changeMonth: true,
                    changeYear: true,
                    yearRange: '1990:c'
                },
                $.datepicker.regional['ru']
            );
        });

    };

});