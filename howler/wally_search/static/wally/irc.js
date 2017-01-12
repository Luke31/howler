/**
 * Created by Lukas on 29.11.2016.
 */

$(function () {
    irc.init(); //Init IRC module
});

var irc = (function () {
    var viewformat = 'YYYY/MM/DD HH:mm';

    var init = function () {
        initDetailSubmit();
    };

    /** Init Serach form submit action*/
    var initDetailSubmit = function () {
        $('#js_result').on('click', '#js_result_table .js_submit-span', function() {
            var form = $(this).siblings('form');
            var tr = form.closest('tr');
            var target = tr.find('.js_popover_content');

            // Don't send query if already log cached
            if(target.html().trim() != "")
                return;

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
                        var table = $('#js_result_table').DataTable();
                        var row = table.row(tr);
                        row.child.hide();
                        wally.resultTableToggleChildRows(table,tr); // Update log-entries to child and open it
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
        });
    };

    return {
        init: init
    }
})();