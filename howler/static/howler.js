/**
 * Created by Lukas on 02.12.2016.
 */

$(function () {
    $('#js_lang_select').on('change', function (e) {
        this.form.submit();
    })
});