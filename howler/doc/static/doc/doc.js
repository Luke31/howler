/**
 * Documentation module
 * -Load markdown file and render them in the page
 * Created by Lukas on 07.12.2016.
 */

$(function () {
    doc.init(); //Init doc module
});

var doc = (function () {
    var init = function () {
        initMarkdownRenderer();
    };

    /**
     * Prepare markdown javascript renderer and load markdown
     */
    var initMarkdownRenderer = function () {
        var markdownFile = $('#js_markdown_src').data('content');
        var url = howler.getStaticBaseUrl() + "doc/md/" + markdownFile + ".md";
        showdown.setOption('tables', true);
        $.ajax({
            type: "GET",
            url: url,
            cache: false,
            success: function (data) {
                var converter = new showdown.Converter(),
                    text = data,
                    html = converter.makeHtml(text);
                var target_str = '#js_markdown_target';
                $(target_str).html(html);
                $(target_str).find('table').addClass('table table-nonfluid');
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert(errorThrown);
            },
            complete: function (jqXHR, textStatus) {
            }
        });
    };

    return {
        init: init
    }
})();
