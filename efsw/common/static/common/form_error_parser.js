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
        if ('__all__' in errors && errors.hasOwnProperty('__all__')) {
            nf_err_callback(errors['__all__']);
        }
    }

    function parse_formset(data, formset_prefix, form_err_callback, nf_err_callback, gen_err_callback) {
        try {
            var errors = $.parseJSON(data.errors);
        } catch (err) {
            gen_err_callback(data);
            return;
        }
        if (formset_prefix in errors && errors.hasOwnProperty(formset_prefix)) {
            var formset_errors = errors[formset_prefix];
            formset_errors = formset_errors.map(
                function(form_errors) {
                    for (var p in form_errors) {
                        if (form_errors.hasOwnProperty(p)) {
                            form_errors[p] = form_errors[p].join(' ');
                        }
                    }
                    return form_errors;
                }
            );
            form_err_callback(formset_errors);
        }
        var nf_prefix = formset_prefix + '__all__';
        if ((nf_prefix) in errors && errors.hasOwnProperty(nf_prefix)) {
            nf_err_callback('Ошибка набора ' + formset_prefix + ': ' + errors[nf_prefix].join(' '));
        }
    }

    return {
        parse: parse,
        parse_formset: parse_formset
    };

});