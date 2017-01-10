/**
 * Created by Lukas on 10.01.2017.
 */

$(function () {
    dt_childtoggler.init(); //Init datatable childtoggler main module
});

var dt_childtoggler = (function () {
    var init = function() {
        // Get init-value of search-bar and set to toggler
        var init_val = $('#show_hits_body')[0].checked;
        $('#js_dt_childtoggle').prop('checked', init_val);

        // Enable toggler switcher
        $('#js_dt_childtoggle').on('change', function (e) {
            var table = $(this).closest('#js_result').find('#js_result_table');
            var toggle_col = table.find('td.details-control');
            toggle_col.each(function(){
                this.click();
            });
        });
    };

    return {
        init: init
    }
})();
