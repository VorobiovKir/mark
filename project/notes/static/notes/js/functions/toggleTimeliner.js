// $(document).ready(function() {
//     $('#timeliner span.date-month').click(function(event) {
//         $(this).closest('li').children('ul').toggle('clip', {}, 200);
//     });
// });

function toggeTimeliner(event) {
    $(event.target).closest('li').children('ul').toggle('clip', {}, 200);
}
