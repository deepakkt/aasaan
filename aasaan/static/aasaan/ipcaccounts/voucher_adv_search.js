/**
 * Created by manimaran on 21-12-2016.
 */
button_submit = null;
button_reset = null;
(function($) {

$(document).ready(function() {
    reload();
});

function reset(){
    $("#id_zone option:selected").removeAttr("selected");
    $("#id_account_type option:selected").removeAttr("selected");
    $("#id_rco_voucher_status option:selected").removeAttr("selected");
//    $("#id_np_voucher_status option:selected").removeAttr("selected");
}

function reload(){
     var url = "/admin/ipcaccounts/voucher_refresh?"
     url = url+'zone='+$('#id_zone').val()
     url = url+'&account_type='+$('#id_account_type').val()
     url = url+'&rco_voucher_status='+$('#id_rco_voucher_status').val()
//     url = url+'&np_voucher_status='+$('#id_np_voucher_status').val()
//     console.log(url)
    var options =  {
        "destroy": true,
       "lengthMenu": [ [10, 25, 50, -1], [10, 25, 50, "All"] ],
        autoFill: true,
        dom: 'RBlfrtip',
        buttons: [
            {
                extend: 'copyHtml5',
                exportOptions: {
                    columns: [ 0, ':visible' ]
                },
            },
            {
                extend: 'excelHtml5',
                exportOptions: {
                    columns: ':visible'
                }
            },
            {
                extend: 'pdfHtml5',
                orientation: 'landscape',
                pageSize: 'LEGAL',
                download: 'open',
                exportOptions: {
                    columns: ':visible'
                }
            },
            'print',
            'colvis'
        ],
        scrollY: 400,
        colReorder: true,
        "ajax": url,
        "columns": [
            { "data": "tracking_no",
                 "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                    if(document.URL.indexOf('npaccountsmaster')>-1){
                        $(nTd).html("<a target='_blank' href='/admin/ipcaccounts/npaccountsmaster/"+oData.id+"/change/'>"+oData.tracking_no+"</a>");
                    }
                    else{
                        $(nTd).html("<a target='_blank' href='/admin/ipcaccounts/rcoaccountsmaster/"+oData.id+"/change/'>"+oData.tracking_no+"</a>");
                    }
                  }
            },
            { "data": "account_type" },
            { "data": "nature_of_voucher" },
            { "data": "voucher_type" },
            { "data": "voucher_date" },
            { "data": "head_of_expenses" },
            { "data": "party_name" },
            { "data": "amount" },
            { "data": "utr_no" },
            { "data": "budget_code" },
            { "data": "rco_voucher_status" },
            { "data": "entity_name" },
            { "data": "np_voucher_status" },
            { "data": "zone" },
        ],
        columnDefs: [
            {   "targets": [3,9,11,13],
                "visible": false
            }
        ],
    }

    var table = $('#voucher_table').DataTable(options)
    table.ajax.reload()


}
button_submit = reload;
button_reset = reset;
})(jQuery);

