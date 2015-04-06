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