/**
 * Created by Lukas on 29.11.2016.
 */

$(function () {
    wally.init(); //Init wally module
});

var wally = (function () {
    var viewformat = 'YYYY/MM/DD HH:mm';

    var init = function () {
        initSearchFormSubmit();
        initFixedDateInput();
        initDateFilterSwitcher();
    };

    /** Init Serach form submit action*/
    var initSearchFormSubmit = function () {
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
                    setResultTable();
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
    };

    /** Init fixed date from-to input fields*/
    var initFixedDateInput = function () {
        // ---Fixed Date input---
        //var viewformat = 'YYYY/MM/DD HH:mm';
        var viewlocale = howler.getLanguageCode(); //Get user-language from main module howler
        var fromDateInputSel = '#datetimepicker-from';
        var toDateInputSel = '#datetimepicker-to';
        $(fromDateInputSel).datetimepicker({
            locale: viewlocale,
            format: viewformat
        });
        $(toDateInputSel).datetimepicker({
            useCurrent: false, //Important! See issue #1075
            locale: viewlocale,
            format: viewformat
        });
        $(fromDateInputSel).on("dp.change", function (e) {
            $('#datetimepicker-to').data("DateTimePicker").minDate(e.date);
        });
        $(toDateInputSel).on("dp.change", function (e) {
            $('#datetimepicker-from').data("DateTimePicker").maxDate(e.date);
        });

        fillToday($('#datetimepicker-to>input'));
        function fillToday(target) {
            var now = moment().format(viewformat);
            target.val(now);
            target.attr("placeholder", now);
        }
    };

    /**Init switch for selection between sliding-filter or fixed date filter*/
    var initDateFilterSwitcher = function () {
        // ---Date-filter SWITCHER---
        $('#use_sliding_value').on('change', function (e) {
            displayCorrectDateType();
        });
        displayCorrectDateType();

        function displayCorrectDateType() {
            var use_sliding_value = parseInt($('#use_sliding_value').val());
            if (use_sliding_value) {
                $('.js_date_fixed').hide();
                $('.js_date_sliding_value').show();
            } else {
                $('.js_date_sliding_value').hide();
                $('.js_date_fixed').show();
            }
        }
    };

    /** Make result-table a DataTable (https://datatables.net/) with collapsed detail informations*/
    var setResultTable = function setResultTable() {
        var targetTableSel = '#js_result_table';
        var table = $(targetTableSel).DataTable({
            //responsive: true
            "language": {
                "url": "static/wally/datatables/"+howler.getLanguageCode()+".json"
            }
        });
        $(targetTableSel).find('tbody').on('click', 'td.details-control', function () {
            var tr = $(this).closest('tr');
            var row = table.row(tr);

            if (row.child.isShown()) {
                // This row is already open - close it
                row.child.hide();
                tr.removeClass('shown');
            }
            else {
                // Open this row
                var extra_data = tr.find('.js_popover_content').html();
                row.child(extra_data).show();
                tr.addClass('shown');
            }
        });
    };

    return {
        init: init
    }
})();