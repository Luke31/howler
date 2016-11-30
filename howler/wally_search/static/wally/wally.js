/**
 * Created by Lukas on 29.11.2016.
 */

//Search
$(function () {
    var viewformat = 'YYYY/MM/DD HH:mm';
    var viewlocale = 'ja';

    $('#datetimepicker-from').datetimepicker({
        locale: viewlocale,
        format: viewformat
    });
    $('#datetimepicker-to').datetimepicker({
        useCurrent: false, //Important! See issue #1075
        locale: viewlocale,
        format: viewformat
    });
    $("#datetimepicker-from").on("dp.change", function (e) {
        $('#datetimepicker-to').data("DateTimePicker").minDate(e.date);
    });
    $("#datetimepicker-to").on("dp.change", function (e) {
        $('#datetimepicker-from').data("DateTimePicker").maxDate(e.date);
    });
});

// Results:
$(function () {
    $('.js_hit').on('click', function () {
        $(this).siblings('tr.js_hit_content').find('div.js_text').toggle();
    });

    $('.js_showmail_btn').on('click', function () {
        event.preventDefault();
        $(this).siblings('div.js_text').toggle();
    });
});