'use strict';

// warning use only in model change screens with one master form
// not tested on multi-form settings!

var aasaan = window.aasaan || {};

aasaan.disable_notes = function () {
    for (var i=0; i < aasaan.base_form.elements.length; i++) {
        // console.log(aasaan.base_form.elements[i].id);
        if (aasaan.base_form.elements[i].type === "select-one" || aasaan.base_form.elements[i].type === "textarea") {
            if ((aasaan.base_form.elements[i].id.endsWith('note_type')) || (aasaan.base_form.elements[i].id.endsWith('-note'))) {
                if (!aasaan.base_form.elements[i].id.contains('__prefix__')) {
                    aasaan.base_form.elements[i].disabled = true;
                }
            }
        }
    }
};

aasaan.enable_notes = function () {
    for (var i=0; i < aasaan.base_form.elements.length; i++) {
        // console.log(aasaan.base_form.elements[i].id);
        if (aasaan.base_form.elements[i].type === "select-one" || aasaan.base_form.elements[i].type === "textarea") {
            if ((aasaan.base_form.elements[i].id.endsWith('note_type')) || (aasaan.base_form.elements[i].id.endsWith('-note'))) {
                if (!aasaan.base_form.elements[i].id.contains('__prefix__')) {
                    aasaan.base_form.elements[i].disabled = false;
                }
            }
        }
    }
};

window.addEventListener("load", function (e) {
    // do the auto population only for new schedules. leave existing schedules untouched
    if (document.URL.endsWith('/change/')) {
        aasaan.base_form = document.forms[0]
        aasaan.base_form.addEventListener('submit', aasaan.enable_notes, false);
        
        aasaan.disable_notes();
    }
});