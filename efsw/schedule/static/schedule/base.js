define(['jquery', 'knockout', 'common/modal_loader'], function($, ko, ml) {

    var view_model;

    return function(conf) {
        $(document).ready(function() {
            // регистрируем обработчик нажатия
            $('#lineup_new_modal_switch').on('click', function () {
                // загружаем содержимое модального окна
                ml(conf.urls.lineup_new_part_modal(), function(modal_container, already_loaded) {
                    if (modal_container) {
                        if (typeof view_model == 'undefined') {
                            // загружаем модель, связанную с модальным окном
                            require(['schedule/model_lineup_new'], function(model) {
                                view_model = new model(conf.urls);
                                // привязываем модель к содержимому модального окна
                                ko.applyBindings(view_model, modal_container.children()[0]);
                                // и показываем окошко
                                modal_container.modal();
                            });
                        } else {
                            if (!already_loaded) {
                                ko.applyBindings(view_model, modal_container.children()[0]);
                            }
                            modal_container.modal();
                        }
                    }
                });
            });
        });
    }

});