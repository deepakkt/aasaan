
var url='';
var span_ID='';
function setURL(txtURL,txtSpanId) { 
    url = txtURL;
	span_ID=txtSpanId;
	console.log('------Start setURL method------');
    console.log('URL :->'+url+'\t Span ID :->'+span_ID);
    console.log('------End   setURL method------');
	return true;
}

$(document).ready(function(){
   for(var i=4;i<=12;i++){
    $("#id_button"+i).hide();
   }	
   $('button[type="submit"]').on('click', function() {   
        console.log('------Start jQuery on click method------');
        console.log('URL  :->'+url);
        console.log('------End   jQuery on click method------');
        $.post(url,
        {
          name: "Donald Duck",
          city: "Duckburg"
        },
        function(data,status){
            console.log('------Start Response------');
            console.log("Data: " + data + "\nStatus: " + status);
            console.log('------End   Response------');
            
            if(status=='success'){		  
			  $("#"+span_ID).html(data).addClass('success').slideUp("slow").slideDown("slow");		  
			}else if(status=='error'){		  
			  $("#"+span_ID).html(data).addClass('error').slideUp("slow").slideDown("slow");		  
			}else if(status=='running'){          	
			  $("#"+span_ID).html(data).addClass('running').slideUp("slow").slideDown("slow");		  
			}
			else{
			  $("#"+span_ID).html(data).slideUp("slow").slideDown("slow");		  
			}
        });
    });
});
