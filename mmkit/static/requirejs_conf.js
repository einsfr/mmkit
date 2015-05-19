var require = {
    baseUrl: '/static',
    paths: {
        bootstrap: 'vendor/bootstrap/js/bootstrap.min',
        jquery: 'vendor/jquery/jquery.min',
        jquery_ui: 'vendor/jquery-ui/jquery-ui.min',
        knockout: 'vendor/knockout/knockout',
        tinycolor: 'vendor/tinycolor/tinycolor'
    },
    shim: {
        bootstrap: { deps: ['jquery'] }
    }
};