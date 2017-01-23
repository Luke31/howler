/**
 * IRC-module to load IRC log history close to a given log-entry.
 * -Provide function to get child-content for results.
 *  This function is called from wally.js (loadPopoverContent) to load child-content.
 * Created by Lukas on 29.11.2016.
 */

$(function () {
    irc.init(); //Init IRC module
});

var irc = (function () {
    var viewformat = 'YYYY/MM/DD HH:mm';

    var init = function () {
        checkSetDayMode();
        $('#day_mode').on('change', function (e) {
            checkSetDayMode();
        });
    };

    /**
     * This callback type is called `loadingFinishedCallback` and is displayed as a global symbol.
     *
     * @callback loadingFinishedCallback
     * @param {jQuery} tr - tr-row for which to show child-content
     * @param row - DataTables row for which to show child-content
     */

    /**
     * Load IRC-logs history as child-content for IRC resulttable. Eventually executes callback when loading finished
     * @param {jQuery} form - form to use for loading child content
     * @param {jQuery} tr - tr-row for which to get child-content
     * @param row - DataTables row for which to get child-content
     * @param {loadingFinishedCallback} cbFillExtraDataAndShowChild - Callback called when loading finished
     */
    var loadPopoverContent = function (form, tr, row, cbFillExtraDataAndShowChild) {
        var target = tr.find('.js_popover_content');
        //Content already loaded? => Just open childrow and return
        if (target.html().trim() != "") {
            cbFillExtraDataAndShowChild(tr, row);
            return;
        }

        // Load logs close to entry
        form.submit(function (e) {
            var url = $(this).attr('action');

            $(".loading").show();
            $.ajax({
                type: "GET",
                url: url,
                data: form.serialize(), // serializes the form's elements.
                success: function (data) {
                    target.html(data);
                    cbFillExtraDataAndShowChild(tr, row);
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
        form.submit();
    };

    /**
     * If day mode is enabled, some sorting-fields shall not be used (e.g. username)
     */
    var checkSetDayMode = function () {
        var isDayMode = $('#day_mode')[0].checked;
        if (isDayMode) {
            $('.js_day_mode_unsupported').prop('disabled', true);
        } else {
            $('.js_day_mode_unsupported').prop('disabled', false);
        }
    };

    return {
        init: init,
        loadPopoverContent: loadPopoverContent //Called from wally.js to load child-content
    }
})();