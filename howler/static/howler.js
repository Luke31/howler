/**
 * Howler main module
 * Created by Lukas on 02.12.2016.
 */

$(function () {
    howler.init(); //Init howler main module
});

var howler = (function () {
    /**
     * General Javascript initialization function for whole howler-application
     */
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

    /**
     * Get current langauge code
     * @returns {*|jQuery} language code "en"/"ja"
     */
    var getLanguageCode = function() {
        return $('#js_page_settings').data('language-code');
    };

    /**
     * Get base-url of static files
     * @returns {*|jQuery} Base-url of static files
     */
    var getStaticBaseUrl = function() {
        return $('#js_page_settings').data('static-baseurl');
    };

    return {
        getLanguageCode: getLanguageCode,
        getStaticBaseUrl: getStaticBaseUrl,
        init: init
    }
})();
