# mmkit

## Рекомендации по настройке среды разработки

### PyCharm

1. Поскольку этот проект использует разные конфигурации для тестирования, разработки и непосредственного использования,
   для нормального запуска нужно явно указать значение DJANGO_SETTINGS_MODULE в списке "Environment variables". Лучше
   всего это сделать в секции "Defaults" ("Run/Debug Configurations") как для "Django tests", так и "Django server" -
   тогда все создаваемые в дальнейшем конфигурации (в том числе - создаваемые динамически самим PyCharm) будут
   автоматически наследовать эти значения: **Django tests** - *DJANGO_SETTINGS_MODULE=mmkit.conf.test*, **Django
   server** - *DJANGO_SETTINGS_MODULE=mmkit.conf.dev*.