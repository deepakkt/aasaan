jQuery(function($){ 
	//on document.ready
    $( "#id_event_start_date" ).datepicker({dateFormat: "yy-mm-dd"});
    $( "#id_event_end_date" ).datepicker({dateFormat: "yy-mm-dd"});
		   
    	$("form").submit(function(event){
		var begD = $.datepicker.parseDate('yy-mm-dd', $('#id_event_start_date').val());
		var endD = $.datepicker.parseDate('yy-mm-dd', $('#id_event_end_date').val());
			  
		if(endD==null){				 
			$('#id_event_end_date').val($('#id_event_start_date').val());
			return false;
		}	  
	    if (begD > endD) {
			$( "#id_enddate").text( "End date must be after Begin date..." ).show();
			event.preventDefault();
			$( "#id_event_end_date" ).focus();
		}	  
				
	});
		   
})

function invalidMsg(textbox) {
    var errmsg='';
	if((textbox.validity.patternMismatch)){
	    if(textbox.id=='id_number_of_people'){
		   errmsg='Please enter only numbers';
        }
		if(textbox.id=='id_event_start_date'){
		   errmsg='Please follow yyyy-mm-dd format';
        }
	    if(textbox.id=='id_event_end_date'){
		   errmsg='Please follow yyyy-mm-dd format';
        }
        if(textbox.id=='id_submitter_mobile'){					
		    errmsg='Please enter a valid 10-digit mobile number';	
		}
        if(textbox.id=='eomob'){					
		    errmsg='Please enter a valid 10-digit mobile number\n or 11-digit land line number along with code';	
		}
        if(textbox.id=='id_ashram_contact_mobile'){					
		    errmsg='Please enter a valid 10-digit mobile number';	
	    }		
	}
    textbox.setCustomValidity(errmsg);
	return true;
}

function createDropDownLists() {
	var jyreg = document.getElementById('id_zone');
	jyreg.options.length = 0;
	createOption(jyreg, 'Choose', '');
	for (var i=0;i < myzones.length;i++) {
		createOption(jyreg, myzones[i].zone, myzones[i].zone);
	}
}

function createOption(ddl, text, value) {
		var opt = document.createElement('option');
		opt.value = value;
		opt.text = text;
		ddl.options.add(opt);
}

function configureDropDownLists(yreg,cen) {
		cen.options.length = 0;
		if(yreg.value==''){
		   createOption(cen, 'Please choose from above', '');
		   return;
		}
		for (var i=0;i < myzones.length;i++) {
		   if(myzones[i].zone==yreg.value){
			  if(myzones[i].centers.length!=0){
				   for(var j=0; j < myzones[i].centers.length; j++){
					createOption(cen, myzones[i].centers[j], myzones[i].centers[j]);
					}
					return;
			   }
			   else{
				   createOption(cen, 'No centers', 'No centers');
				   return;
			   }
			}

		}
}

$(document).ready(function() {
   createDropDownLists();
});