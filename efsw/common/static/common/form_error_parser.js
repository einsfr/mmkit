define(['jquery'], function($) {

    function parse(data, field_err_callback, nf_err_callback, gen_err_callback) {
        try {
            var errors = $.parseJSON(data.errors);
        } catch (err) {
            gen_err_callback(data);
            return;
        }
        for (var p in errors) {
            if (errors.hasOwnProperty(p)) {
                errors[p] = errors[p].map(
                    function(e) {
                        if (typeof e == 'object' && 'message' in e) {
                            return e.message;
                        } else {
                            return e;
                        }
                    }
                ).join(' ');
            }
        }
        field_err_callback(errors);
        if ('__all__' in errors) {
            nf_err_callback(errors['__all__']);
        }
    }

    return {
        parse: parse
    };

});