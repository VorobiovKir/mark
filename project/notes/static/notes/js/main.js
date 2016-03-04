angular
    .module('MainApp', ['ngCookies'])
        .config(function($httpProvider, $interpolateProvider) {
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
            $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
            $interpolateProvider.startSymbol('[[').endSymbol(']]');
        })
    .controller('TimelinerController', TimelinerController)
    .controller('MainController', MainController)
    .controller('PanelController', ['$cookies', PanelController]);
