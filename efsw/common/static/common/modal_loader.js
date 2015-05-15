define(['jquery', 'knockout', 'bootstrap'], function($, ko) {

    var cache = {};
    var loaded_url;
    var loaded_model;
    var modal_container = $('#common_modal');

    function update_modal(content, callback) {
        modal_container.empty();
        modal_container.append(content);
        callback(modal_container, false);
    }

    function get(url, settings, callback) {
        if (typeof settings == 'function') {
            // Значит - это callback
            callback = settings;
            settings = {};
        }
        var already_loaded = (loaded_url == url);
        loaded_url = url;
        if (already_loaded) {
            callback(modal_container, true);
        } else {
            if (url in cache) {
                update_modal(cache[url], callback);
            } else {
                $.ajax(url, settings).done(function(result) {
                    cache[url] = result;
                    update_modal(result, callback);
                }).fail(function(jqXHR, textStatus) {
                    alert('При загрузке возникла ошибка: ' + textStatus);
                });
            }
        }
    }

    function get_with_model(url, settings, model_name, callback) {
        if (typeof model_name == 'function' && typeof callback == 'undefined') {
            callback = model_name;
            model_name = settings;
            settings = {};
        }
        var get_callback = function(modal_container, already_loaded) {
            if (already_loaded) {
                callback(modal_container, true, loaded_model);
            } else {
                require([model_name], function(model) {
                    loaded_model = new model();
                    ko.applyBindings(loaded_model, modal_container.children()[0]);
                    callback(modal_container, false, loaded_model);
                });
            }
        };
        get(url, settings, get_callback);
    }

    return {
        get: get,
        get_with_model: get_with_model
    };

});