define(['jquery', 'bootstrap'], function($) {

    var cache = {};

    function update_modal(content, callback) {
        var container = $('#common_modal');
        container.empty();
        container.append(content);
        callback(container);
    }

    return function(url, settings, callback) {
        if (typeof settings == 'function') {
            // Значит - это callback
            callback = settings;
        }
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
    };

});