define(['jquery'], function($) {

    function parse(data, err_observable, nf_err_observable) {
        try {
            var errors = $.parseJSON(data.errors);
        } catch (err) {
            nf_err_observable(data);
            return;
        }
        nf_err_observable('');
        for (var p in errors) {
            if (errors.hasOwnProperty(p)) {
                errors[p] = errors[p].map(function(e) { return e.message; }).join(' ');
            }
        }
        err_observable(errors);
    }

    return {
        parse: parse
    };

});