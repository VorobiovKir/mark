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
    .filter('toSec', function($filter) {
        return function(input) {
            var result = new Date(input).getTime();
            return result || input;
        };
    })
    .filter('toArray', function() { return function(obj) {
        if (!(obj instanceof Object)) return obj;
        return _.map(obj, function(val, key) {
            return Object.defineProperty(val, '$key', {__proto__: null, value: key});
        });
    }})
    .filter('orderByMonthName', function() {
        return function(items, field, reverse) {
            var months = ['jan', 'feb', 'mar', 'apr', 'may', 'june', 'july', 'aug', 'sept', 'oct', 'nov', 'dec']
            var filtered = [];
            for (var k in items) {
                filtered.push(k);
            }
            filtered.sort(function(a, b) {
                return months.indexOf(a) - months.indexOf(b);
            })

            return filtered
        };
    })
    .filter('orderByNum', function() {
        return function(items, field, reverse) {
            var filtered = [];
            for (var k in items) {
                filtered.push(k);
            }
            return filtered.sort();
        };
    });

    // .filter('orderByKeyNum', function() {
    //     return function(items, field, reverse) {
    //         console.log('**********');
    //         console.log(items);
    //         var filtered = [];
    //         for (var k in items.mar) {
    //             filtered.push(k);
    //         }
    //         console.log('---------');
    //         console.log(filtered);
    //         // var filtered = [];
    //         // for (var k in items) {
    //         //     filtered.push(k);
    //         // }
    //         // filtered.sort();
    //         // if(reverse) filtered.reverse();
    //         // var result = [];
    //         // for (var i in filtered) {
    //         //     result.push({i:items[i]});
    //         // }
    //         // console.log(result);
    //         // return result;
    //     };
    // });
