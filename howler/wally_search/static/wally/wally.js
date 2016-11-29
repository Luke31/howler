/**
 * Created by Lukas on 29.11.2016.
 */
$(function () {
    $('.js_hit').on('click', function () {
        $(this).siblings('tr.js_hit_content').find('div.js_text').toggle();
    });

    $('.js_showmail_btn').on('click', function () {
        event.preventDefault();
        $(this).siblings('div.js_text').toggle();
    });
});