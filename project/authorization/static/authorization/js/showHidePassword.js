$(document).ready(function() {

    'use strict';

    $('#showHidePassCheckbox').click(function() {
        let target_elem = $('#password');
        let input_type = (target_elem.attr('type') === 'password') ? 'text' : 'password'

        target_elem.attr('type', input_type);
    });
});
