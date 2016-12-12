/**
 * Created by Lukas on 07.12.2016.
 */

var settings = (function () {
    /**Transfer all saved synonyms (PostgreSQL) to Elasticsearch index*/
    var synonymTransfer = function () {
        var url = $(this).data('url');
        $(".loading").show();
        $.ajax({
            type: "GET",
            url: url,
            data: $("#js_searchform").serialize(), // serializes the form's elements.
            success: function (data) {
                var success_text = gettext('Successfully updated elasticsearch index');
                $("#js_result_container").show();
                //alert(success_text);
                $("#js_result").html(success_text);
                $("#js_result_container").fadeOut(5000);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert(errorThrown);
            },
            complete: function (jqXHR, textStatus) {
                $(".loading").hide();
            }
        });
    };

    return {
        synonymTransfer: synonymTransfer
    }
});
