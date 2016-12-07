/**
 * Created by Lukas on 29.11.2016.
 */

//Search
$(function () {
    // ---Submit---
    $("#js_searchform").submit(function (e) {
        var url = $(this).attr('action');
        $(".loading").show();
        $.ajax({
            type: "GET",
            url: url,
            data: $("#js_searchform").serialize(), // serializes the form's elements.
            success: function (data) {
                $("#js_result").html(data);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert(errorThrown);
            },
            complete: function (jqXHR, textStatus) {
                $(".loading").hide();
            }
        });

        e.preventDefault(); // avoid to execute the actual submit of the form.
    });

    // ---Fixed Date input---
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

    fill_today($('#datetimepicker-to>input'));
    function fill_today(target) {
        var now = moment().format(viewformat);
        target.val(now);
        target.attr("placeholder", now);
    }

    // ---Date-filter SWITCHER---
    $('#use_sliding_value').on('change', function (e) {
        display_correct_date_type();
    });
    display_correct_date_type();

    function display_correct_date_type() {
        var use_sliding_value = parseInt($('#use_sliding_value').val());
        if (use_sliding_value) {
            $('.js_date_fixed').hide();
            $('.js_date_sliding_value').show();
        } else {
            $('.js_date_sliding_value').hide();
            $('.js_date_fixed').show();
        }
    }
});



