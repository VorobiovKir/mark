function orderByNum() {
    return function(items, field, reverse) {
        var filtered = [];
        for (var k in items) {
            filtered.push(k);
        }
        return filtered.sort();
    };
}

function orderByMonthName() {
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
}

function toArray() {
    return function(obj) {
        if (!(obj instanceof Object)) return obj;
        return _.map(obj, function(val, key) {
            return Object.defineProperty(val, '$key', {__proto__: null, value: key});
        });
    }
}

function toSec($filter) {
    return function(input) {
        var result = new Date(input).getTime();
        return result || input;
    };
}
