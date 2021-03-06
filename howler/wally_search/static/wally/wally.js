/**
 * Wally-module
 * -Prepare search form for Email and IRC-search (init form submit action, date fields)
 * -Render result-table as Javascript Datatable (https://datatables.net)
 * -Set result row-color by its score
 * -Result-table has collapsed detail-infos, these may be provided already in the result or
 *  lazy-loaded using the hook-function
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
        initSyntaxInfoToggler();
    };

    /**
     * Init Serach form submit action
     */
    var initSearchFormSubmit = function () {
        // ---Submit---
        $("#js_searchform").submit(function (e) {
            var url = $(this).attr('action');
            var form = $("#js_searchform");
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

    /**
     * Init fixed date from-to input fields
     */
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

    /**
     * Init switch for selection between sliding-filter or fixed date filter
     */
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

    /**
     * Make result-table a DataTable (https://datatables.net/) with collapsed detail informations
     */
    var setResultTable = function () {
        var targetTableSel = '#js_result_table';

        // FEATURE READY: Get order by selected col and apply to datatables
        //var sortField = $('#sort_field').val();
        //var sortColDict = {'date':3,'fromEmail.keyword':4,'toEmail.keyword':5,'_score':7,
        //'channel.keyword':1,'@timestamp':2,'username.keyword':3};
        //var orderColIdx = sortColDict[sortField];
        //if(typeof(orderColIdx) === 'undefined')
        //    orderColIdx = $(targetTableSel).find('th').length - 1; //Ignore toggle-column

        //Grouping column
        var groupCol = $(targetTableSel).find('.js_datatables_hidden').index();
        var columnDefs = [];
        var drawCallback;
        if (groupCol > 0) {
            columnDefs = [{"visible": false, "targets": groupCol}];
            drawCallback = function (settings) {
                var api = this.api();
                var rows = api.rows({page: 'current'}).nodes();
                var last = null;

                api.column(groupCol, {page: 'current'}).data().each(function (group, i) {
                    var cols = table.columns().visible().length - 1; //
                    if (last !== group) {
                        $(rows).eq(i).before(
                            '<tr class="group"><td colspan="' + cols + '">' + group + '</td></tr>'
                        );

                        last = group;
                    }
                });
            }
        }

        // FEATURE READY: Order by the grouping
        // $(targetTableSel).find('tbody').on('click', 'tr.group', function () {
        //     var currentOrder = table.order()[0];
        //     if (currentOrder[0] === groupCol && currentOrder[1] === 'asc') {
        //         table.order([groupCol, 'desc']).draw();
        //     }
        //     else {
        //         table.order([groupCol, 'asc']).draw();
        //     }
        // });

        //Create table
        var table = $(targetTableSel).DataTable({
            "columnDefs": columnDefs,
            //responsive: true
            "language": {
                "url": howler.getStaticBaseUrl() + "wally/datatables/" + howler.getLanguageCode() + ".json"
            },
            "pageLength": 25,
            "lengthMenu": [[10, 15, 25, 50, 100], [10, 15, 25, 50, 100]],
            "drawCallback": drawCallback,
            "stateSave": !isDayMode() // Save in localstorage for 2h ttps://datatables.net/examples/basic_init/state_save.html
            //"order": [[orderColIdx, "desc"]]
        });

        $(targetTableSel).find('tbody').on('click', 'td.details-control', function () {
            var tr = $(this).closest('tr');
            resultTableToggleChildRows(table, tr);
        });

        setRowColor(targetTableSel);

        // Show child-rows if desired
        var childToggle = $('#js_dt_childtoggle');
        if (childToggle.length && childToggle[0].checked) {
            table.rows().every(function (rowIdx, tableLoop, rowLoop) {
                var tr = this.nodes().to$();
                resultTableToggleChildRows(table, tr);
            });
        }
    };

    /**
     * Toogle child row
     * @param table - DataTables-table for which to toggle child-row
     * @param {jQuery} tr - tr-row to toggle
     */
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

    /** Parses child-row content and shows child
     * @param {jQuery} tr - tr-row for which to show child-content
     * @param row - DataTables row for which to show child-content
     */
    var cbFillExtraDataAndShowChild = function (tr, row) {
        var extra_data = tr.find('.js_popover_content').html();
        row.child(extra_data).show();
        tr.addClass('shown');
    };

    /**
     * Load content for child-row
     * Searches for form in row to load external content for child-row:
     * If found, call of this form is delegated to the specific functionModule. The functionModule.loadPopoverContent
     *  also calls the display-child-method which is passed as a callback-function.
     * If not found, existing child-content is shown.
     * @param {jQuery} tr - tr-row for which to get child-content
     * @param row - DataTables row for which to get child-content
     */
    var loadPopoverContent = function (tr, row) {
        var form = tr.find('form.js_loadpopoverontent_form');

        //Form available to load additional content?
        if (form.length) {
            var module = form.data('functionModule');
            //Load content, provide function-hook to call when load finished (shows child-row)
            window[module]["loadPopoverContent"](form, tr, row, cbFillExtraDataAndShowChild);
        } else {
            //Just open childrow (child-content already in result)
            cbFillExtraDataAndShowChild(tr, row);
        }
    };

    /**
     * Set row color according to score
     * @param {string} targetTableSel - string as jquery-selector for table to set row color
     */
    var setRowColor = function (targetTableSel) {
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

    /**
     * Return True if IRC search day-mode is on
     * @returns {boolean|*} Day mode on
     */
    var isDayMode = function(){
        var dayModeCheckbox = $('#day_mode');
        return dayModeCheckbox.length && dayModeCheckbox[0].checked;
    };

    /**
     * Toggle the display of the syntax-info-box
     */
    var initSyntaxInfoToggler = function(){
      $('.js_info_query_syntax_toggle').on('click', function(){
          $('.js_info_query_syntax').slideToggle();
      });
    };

    return {
        init: init,
        isDayMode: isDayMode
    }
})();