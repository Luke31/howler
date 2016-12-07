/**
 * Created by Lukas on 07.12.2016.
 */
$(function () {
    // $('#js_transfer').confirmation({
    //     btnOkLabel: gettext('Yes'),
    //     btnCancelLabel: gettext('No'),
    //     title: gettext('Really update Elasticsearch index? The search will not be available during the update.'),
    //     onCofirm: synonym_transfer()
    //     // other options
    // });
});

function synonym_transfer() {
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
}
