/**
 * Created by Lukas on 07.12.2016.
 */

$(function () {
    doc.init(); //Init doc module
});

var doc = (function () {
    var init = function () {
        initMarkdownRenderer();
    };

    /**Prepare markdown javascript renderer*/
    var initMarkdownRenderer = function () {
        var markdownFile = $('#js_markdown_src').data('content');
        var url = howler.getStaticBaseUrl() + "doc/md/" + markdownFile + ".md";
        // $(".loading").show();
        $.ajax({
            type: "GET",
            url: url,
            success: function (data) {
                var converter = new showdown.Converter(),
                    text = data,
                    html = converter.makeHtml(text);
                $('#js_markdown_target').html(html);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert(errorThrown);
            },
            complete: function (jqXHR, textStatus) {
                // $(".loading").hide();
            }
        });
    };

    return {
        init: init
    }
})();
