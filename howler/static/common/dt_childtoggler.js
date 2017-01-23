/**
 * Created by Lukas on 10.01.2017.
 */

$(function () {
    dt_childtoggler.init(); //Init datatable childtoggler main module
});

var dt_childtoggler = (function () {
    var init = function() {
        // Enable toggler switcher
        $('#js_result').on('change', '#js_dt_childtoggle', function (e) {
            updateSession($(this));
            var table = $(this).closest('#js_result').find('#js_result_table');
            var toggle_col = table.find('td.details-control');
            toggle_col.each(function(){
                this.click();
            });
        });

        // Enable session-update
    };

    /**
     * Update selected child-toggle value to django session if ajax-form available
     * @param {jQuery} checkbox - Current selected state
     */
    var updateSession = function(checkbox){
        var form = checkbox.parents('#js_updatesessionform');

        if (form.length) {
            // Update session values
            form.submit(function (e) {
                var url = $(this).attr('action');

                //$(".loading").show();
                $.ajax({
                    type: "GET",
                    url: url,
                    data: form.serialize(), // serializes the form's elements.
                    success: function (data) {
                        console.log(data.success);
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        alert(errorThrown);
                    },
                    complete: function (jqXHR, textStatus) {
                        //$(".loading").hide();
                    }
                });

                e.preventDefault(); // avoid to execute the actual submit of the form.
            });
            form.submit();
        }
    };

    return {
        init: init
    }
})();
