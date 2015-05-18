define(['jquery'], function($) {

    function parse(data, err_observable, nf_err_observable) {
        try {
            var errors = $.parseJSON(data.errors);
        } catch (err) {
            if (typeof nf_err_observable != 'undefined') {
                nf_err_observable(data);
            } else {
                alert(data);
            }
            return;
        }
        for (var p in errors) {
            if (errors.hasOwnProperty(p)) {
                errors[p] = errors[p].map(function(e) { return e.message; }).join(' ');
            }
        }
        err_observable(errors);
        if (typeof nf_err_observable != 'undefined') {
            if ('__all__' in errors) {
                nf_err_observable(errors['__all__']);
            } else {
                nf_err_observable('');
            }
        }
    }

    return {
        parse: parse
    };

});