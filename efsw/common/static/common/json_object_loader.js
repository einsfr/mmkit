define(['jquery', 'common/ajax_json_request'], function($, ajr) {

    var object_cache = {};

    function load(url, obj_class, load_callback, fail_callback, err_callback, options) {
        if (typeof options == 'undefined') {
            options = {};
        }
        var default_options = {
            ignore_cache: false,
            ajax_settings: {}
        };
        options = $.extend(true, default_options, options);
        if (!options.ignore_cache) {
            if (url in object_cache) {
                load_callback($.extend({}, object_cache[url]));
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
            options.ajax_settings,
            function(response) {
                var loaded_obj = new obj_class(response.data);
                object_cache[url] = $.extend({}, loaded_obj);
                load_callback(loaded_obj);
            },
            err_callback,
            fail_callback
        );
    }

    return {
        load: load
    };

});