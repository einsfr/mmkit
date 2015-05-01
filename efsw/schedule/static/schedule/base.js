define(['jquery', 'knockout', 'common/modal_loader'], function($, ko, ml) {

    return function(conf) {
        $(document).ready(function() {
            // регистрируем обработчик нажатия
            $('#lineup_new_modal_switch').on('click', function () {
                // загружаем содержимое модального окна
                ml(conf.urls.lineup_new_part_modal(), function(modal_container) {
                    if (modal_container) {
                        // загружаем модель, связанную с модальным окном
                        require(['schedule/model_lineup_new'], function(model) {
                            // привязываем модель к содержимому модального окна
                            ko.applyBindings(new model(conf), modal_container.children()[0]);
                            // и показываем окошко
                            modal_container.modal();
                        });
                    }
                });
            });
        });
    }

});