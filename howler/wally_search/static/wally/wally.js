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
            var form = $("#js_searchform")
            $(".loading").show();
            $.ajax({
                type: "GET",
                url: url,
                data: form.serialize(), // serializes the form's elements.
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
    var setResultTable = function () {
        var targetTableSel = '#js_result_table';

        //var sortField = $('#sort_field').val();
        //var sortColDict = {'date':3,'fromEmail.keyword':4,'toEmail.keyword':5,'_score':7,
        //'channel.keyword':1,'@timestamp':2,'username.keyword':3};
        //var orderColIdx = sortColDict[sortField];
        //if(typeof(orderColIdx) === 'undefined')
        //    orderColIdx = $(targetTableSel).find('th').length - 1; //Ignore toggle-column
        var table = $(targetTableSel).DataTable({
            //responsive: true
            "language": {
                "url": howler.getStaticBaseUrl() + "wally/datatables/" + howler.getLanguageCode() + ".json"
            },
            "pageLength": 15,
            "lengthMenu": [[10, 15, 25, 50, 100], [10, 15, 25, 50, 100]],
            //"order": [[orderColIdx, "desc"]]
        });

        $(targetTableSel).find('tbody').on('click', 'td.details-control', function () {
            var tr = $(this).closest('tr');
            resultTableToggleChildRows(table, tr);
        });

        setRowOpacity(targetTableSel);

        // Show child-rows if desired
        if ($('#show_hits')[0].checked) {
            table.rows().every(function (rowIdx, tableLoop, rowLoop) {
                var tr = this.nodes().to$();
                resultTableToggleChildRows(table, tr);
            });
        }
    };

    /** Toogle child rows **/
    var resultTableToggleChildRows = function (table, tr) {
        var row = table.row(tr);
        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            loadPopoverContent(tr, row); //Load additional data if required and available (e.g. IRC Log)
        }
    };

    /** Parses child-row content and shows child **/
    var cbFillExtraDataAndShowChild = function (tr, row) {
        var extra_data = tr.find('.js_popover_content').html();
        row.child(extra_data).show();
        tr.addClass('shown');
    };

    /** Hook to load content for child-row, may be changed from outside **/
    var loadPopoverContent = function (tr, row) {
        var form = tr.find('form.js_loadpopoverontent_form');

        //Form available to laod additional content?
        if (form.length) {
            var module = form.data('functionModule');
            window[module]["loadPopoverContent"](form, tr, row, cbFillExtraDataAndShowChild);
        }else{
            //Just open childrow
            cbFillExtraDataAndShowChild(tr, row);
        }
    };

    /*Set row opacity according to score*/
    var setRowOpacity = function (targetTableSel) {
        var rows = $(targetTableSel).find('tbody tr');
        var max = 0;

        rows.each(function (i) {
            var score = $(this).find('.js_score').html().trim() * 1;
            max = (score > max) ? score : max;
        });

        var min = 0.6;
        rows.each(function (i) {
            var row = $(this);
            var score_td = row.find('.js_score');
            var score = score_td.html().trim() * 1;
            var opacity = score / 100;
            //var opacity = (score / max);  // Used to control tr-opacity
            //row.css('opacity', Math.max(opacity, min)); // Used to control tr-opacity
            var green = '0, 173, 0';
            var red = '184, 82, 81';
            score_td.css('background-color', 'rgba(' + red + ',' + opacity + ')')
        });
    };

    return {
        init: init
    }
})();