define(['jquery'], function($) {

    var object_cache = {};

    function load(url, obj_class, load_callback, fail_callback, err_callback, options) {
        if (typeof options == 'undefined') {
            options = {};
        }
        var default_options = {
            ignore_cache: false,
            ajax_settings: {},
            fail_alert: true,
            err_alert: true
        };
        options = $.extend(true, default_options, options);
        if (!options.ignore_cache) {
            if (url in object_cache) {
                load_callback($.extend({}, object_cache[url]));
                return;
            }
        }
        if (typeof fail_callback == 'undefined') {
            if (options.fail_alert) {
                fail_callback = function(jqXHR, textStatus) {
                    alert('При загрузке объекта возникла ошибка: ' + textStatus);
                };
            } else {
                fail_callback = function() {};
            }
        }
        if (typeof err_callback == 'undefined') {
            if (options.err_alert) {
                err_callback = function(response) {
                    alert(response.data);
                };
            } else {
                err_callback = function() {};
            }
        }
        $.ajax(url, options.ajax_settings).done(function(response) {
            if (response.status == 'ok') {
                var loaded_obj = new obj_class(response.data);
                object_cache[url] = $.extend({}, loaded_obj);
                load_callback(loaded_obj);
            } else {
                err_callback(response);
            }
        }).fail(fail_callback);
    }

    return {
        load: load
    };

});