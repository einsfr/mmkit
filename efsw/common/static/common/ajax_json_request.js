define(['jquery'], function($) {

    function exec(url, settings, ok_callback, err_callback, fail_callback) {
        if (typeof settings == 'function') {
            fail_callback = err_callback;
            err_callback = ok_callback;
            ok_callback = settings;
        }
        $.ajax(url, settings).done(function(response) {
            if (response.status == 'ok') {
                ok_callback(response);
            } else {
                err_callback(response);
            }
        }).fail(function(jqXHR, textStatus, errorThrown) {
            fail_callback(
                'При выполнении запроса произошла ошибка' + (errorThrown ? ': ' + errorThrown : '') +
                ', попробуйте повторить его позднее.'
            );
        });
    }

    return {
        'exec': exec
    }

});