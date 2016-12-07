/**
 * Created by Lukas on 02.12.2016.
 */

// Enable auto-language switcher
$(function () {
    $('#js_lang_select').on('change', function (e) {
        this.form.submit();
    })
});

// Enable Bootstrap confirmation
$('[data-toggle=confirmation]').confirmation({
    rootSelector: '[data-toggle=confirmation]',
    btnOkLabel: gettext('Yes'),
    btnCancelLabel: gettext('No'),
    title: gettext('Are you sure?')
    // other options
});