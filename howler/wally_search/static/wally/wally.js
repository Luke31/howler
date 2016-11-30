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

    $("#js_searchform").submit(function (e) {
        var url = $(this).attr('action');

        $.ajax({
            type: "GET",
            url: url,
            data: $("#js_searchform").serialize(), // serializes the form's elements.
            success: function (data) {
                $("#js_result").html(data);
            }
        });

        e.preventDefault(); // avoid to execute the actual submit of the form.
    });
});
