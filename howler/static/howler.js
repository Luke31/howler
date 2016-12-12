/**
 * Created by Lukas on 02.12.2016.
 */

$(function () {
    howler.init(); //Init howler main module
});

var howler = (function () {
    var init = function() {
        // Enable auto-language switcher
        $('#js_lang_select').on('change', function (e) {
            this.form.submit();
        });

        // Enable Bootstrap confirmation
        $('[data-toggle=confirmation]').confirmation({
            rootSelector: '[data-toggle=confirmation]',
            btnOkLabel: gettext('Yes'),
            btnCancelLabel: gettext('No'),
            title: gettext('Are you sure?')
            // other options
        });
    };

    var getLanguageCode = function() {
        return $('#js_page_settings').data('language-code');
    };

    var getStaticBaseUrl = function() {
        return $('#js_page_settings').data('static-baseurl');
    };


    return {
        getLanguageCode: getLanguageCode,
        getStaticBaseUrl: getStaticBaseUrl,
        init: init
    }
})();
