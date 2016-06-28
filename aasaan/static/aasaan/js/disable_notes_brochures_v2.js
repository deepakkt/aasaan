'use strict';

// warning use only in model change screens with one master form
// not tested on multi-form settings!

var aasaan = window.aasaan || {};

aasaan.disable_notes = function () {
    // this function saves the current textarea notes into a separate area
    // and substitutes them with a simpler text based display. 
    
    aasaan.base_notes_original_HTML = {};
    
    for (var i=0; i < aasaan.base_notes.length; i++) {
        aasaan.base_notes_text = aasaan.base_notes[i].getElementsByTagName('textarea')[0].value;
        aasaan.base_notes_original_HTML[aasaan.base_notes[i].id] = aasaan.base_notes[i].innerHTML;
        aasaan.base_notes[i].innerHTML = "<br /><p>" + aasaan.base_notes_text.replace(/\n/g, "<br />") + "</p><br /><hr />";
        // aasaan.base_notes[i].innerHTML = "<p><pre style=\"color: black; font-size: 1.25em;\">" + aasaan.base_notes_text + "</pre></p><hr />";
    }
    
};

aasaan.submit_dispatch = function (e) {        
    e.preventDefault();
    
    // this section disables the submit buttons after the form has been submitted
    // to avoid multi-clicks
        
    for (var i=0; i < aasaan.submit_elements.length; i++) {
        aasaan.submit_elements[i].disabled = true;
    }
    
    // now put the notes back in the correct perspective with textarea and all
    if (document.URL.endsWith('/change/')) {
        aasaan.append_user();
        aasaan.enable_notes();
    }    
    
    // the following section is needed for very precarious reasons. 
    // because we are preventing default event process, the default
    // form submission doesn't happen. Along with it is lost
    // which button was clicked (it is important as django admin
    // uses that to dispatch the appropriate HTTPResponseRedirect)
    // so we are recreating the 'click' below by adding a new
    // hidden element
    
    var submit_element = document.createElement('input');
    submit_element.type = "hidden";
    submit_element.name = aasaan.submit_clicked_value;
    submit_element.value = aasaan.submit_clicked_value;
    aasaan.base_form.appendChild(submit_element);

    aasaan.base_form.submit();
}

aasaan.enable_notes = function () {    
    // this function reverses what was done by disable_notes
    
    for (var i=0; i < aasaan.base_notes.length; i++) {
        aasaan.base_notes[i].innerHTML = aasaan.base_notes_original_HTML[aasaan.base_notes[i].id];
    }
};

aasaan.append_user = function() {
    // this function will get newly added notes and append the user id with timestamp
    aasaan.new_notes = document.getElementsByClassName('inline-related dynamic-brouchertransfernote_set');
    for (var i=0; i < aasaan.new_notes.length; i++) {

        if (aasaan.new_notes[i].getElementsByTagName('textarea').length > 0) {
            var current_element = aasaan.new_notes[i].getElementsByTagName('textarea')[0];
            if(current_element.value.trim()=='')
                return;
            aasaan.new_notes_text = current_element.value;
            aasaan.new_notes_text += "\n";
            
            var user_div = document.getElementById('user-tools');
            var user_name = user_div.getElementsByTagName('strong')[0].innerHTML;
            
            var note_meta = "\n----------------\n"
            note_meta += "Added by: " + user_name + "\n";
            note_meta += Date(Date.now());
            
            current_element.value = aasaan.new_notes_text + note_meta;
        }
    }        
}


// next three functions capture which button was clicked
// submit, submit and continue, submit and add new
aasaan.submit_clicked_save = function (e) {
    aasaan.submit_clicked_value = '_save';
}

aasaan.submit_clicked_addanother = function (e) {
    aasaan.submit_clicked_value = '_addanother';
}

aasaan.submit_clicked_continue = function (e) {
    aasaan.submit_clicked_value = '_continue';
}

window.addEventListener("load", function (e) {
    aasaan.input_div = document.getElementsByClassName('submit-row')[0];
    aasaan.submit_elements = aasaan.input_div.getElementsByTagName('input');

    for (var i=0; i < aasaan.submit_elements.length; i++) {
        aasaan.submit_elements[i].addEventListener('click', aasaan["submit_clicked" + aasaan.submit_elements[i].name], true);
    }
    
    // do the auto population only for new schedules. leave existing schedules untouched
    if (document.URL.endsWith('/change/')) {        
        aasaan.base_notes = document.getElementsByClassName('inline-related has_original');
        
        if (aasaan.base_notes.length > 0)
            aasaan.disable_notes();
    }
    
    aasaan.base_form = document.forms[0];
    aasaan.base_form.addEventListener('submit', aasaan.submit_dispatch, false);    
});