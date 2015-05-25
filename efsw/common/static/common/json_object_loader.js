define(['jquery', 'common/ajax_json_request'], function($, ajr) {

    var object_cache = {};

    function load(url, ajax_settings, obj_class, ok_callback, err_callback, fail_callback, options) {
        var default_options = {
            ignore_cache: false
        };
        if (typeof options == 'undefined') {
            options = default_options;
        } else {
            options = $.extend(true, default_options, options);
        }
        var cache_key;
        if ('data' in ajax_settings) {
            cache_key = url + $.param(ajax_settings.data);
        } else {
            cache_key = url;
        }
        if (!options.ignore_cache) {
            if (cache_key in object_cache) {
                ok_callback($.extend({}, object_cache[cache_key]));
                return;
            }
        }
        if (typeof fail_callback == 'undefined') {
            fail_callback = function() {};
        }
        if (typeof err_callback == 'undefined') {
            err_callback = function() {};
        }
        ajr.exec(
            url,
            ajax_settings,
            function(response) {
                var loaded_obj = new obj_class(response.data);
                object_cache[cache_key] = $.extend({}, loaded_obj);
                ok_callback(loaded_obj);
            },
            err_callback,
            fail_callback
        );
    }

    return {
        load: load
    };

});