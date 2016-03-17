angular
    .module('MainApp', ['ngCookies'])

        .config(function($httpProvider, $interpolateProvider) {
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
            $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
            $interpolateProvider.startSymbol('[[').endSymbol(']]');
        })
        .config( [
            '$compileProvider',
            function($compileProvider) {
                $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|chrome-extension):/);
            }
        ])

    .controller('MainController', MainController)
    .controller('PanelController', ['$cookies', PanelController])

    .filter('toSec', toSec)
    .filter('toArray', toArray)
    .filter('orderByMonthName', orderByMonthName)
    .filter('orderByNum', orderByNum);
