/**
 * Created by manimaran on 21-12-2016.
 */
refresh_charts = null;
refresh_tables = null;

(function($) {
    isChart = true;
    isChartClicked = true;
    google.charts.load('current', {'packages':['corechart', 'table']});
    google.charts.setOnLoadCallback(drawVisualization);

    function refreshCharts(r_zone) {
        var currentZone = document.getElementById(aasaan_stats_dashboard.report_zone).innerText;
        var clickedZone = r_zone;
        var clickedZoneName = document.getElementById(r_zone).innerText;
        if (currentZone == clickedZoneName && isChartClicked) {
            // active zone was clicked. no action is required
            return
        }
        isChartClicked = true
        refresh(clickedZone, clickedZoneName, r_zone, true);
    }

    function refreshTables(r_zone) {
        var currentZone = document.getElementById(aasaan_stats_dashboard.report_zone).innerText;
        var clickedZone = r_zone;
        var clickedZoneName = document.getElementById(r_zone).innerText;
        if (currentZone == clickedZoneName && isChartClicked==false) {
            // active zone was clicked. no action is required
            return
        }
        isChartClicked = false
        refresh(clickedZone, clickedZoneName, r_zone, false);
    }

    function refresh(clickedZone, clickedZoneName, r_zone, isChart){
        document.getElementById(clickedZone).parentNode.className = "active";
        document.getElementById(aasaan_stats_dashboard.report_zone).parentNode.className = "";
        aasaan_stats_dashboard.report_zone = r_zone;
        pageHeader = document.getElementsByClassName("page-header")[0];
        pageHeader.innerText = "Statistics Dashboard - " + clickedZoneName;
        drawVisualization(clickedZoneName, isChart);
    }
    refresh_charts = refreshCharts;
    refresh_tables = refreshTables;
    function drawVisualization(zone, isChart) {

        if(zone==undefined || zone=='undefined')
            zone='Tamil Nadu'
        if(isChart==undefined || isChart=='undefined')
            isChart=true

        var options = {
          title : '',
          vAxis: {title: 'Participants'},
          hAxis: {title: 'Month'},
          seriesType: 'bars',
          series: {5: {type: 'line'}},
          chartArea: {
                backgroundColor: {
                    stroke: '#4322c0',
                    strokeWidth: 3
                }
            },
          colors: ['#1b9e77', '#d95f02', '#7570b3', '5D6D7E', '#FA1705']
        };
        stats_data = aasaan_stats_dashboard.dashboard_data.statistics;
        if (zone=='Tamil Nadu'){
            ie_data = google.visualization.arrayToDataTable(stats_data.TN_IE)
            other_prg_data = google.visualization.arrayToDataTable(stats_data.TN_OTHER)
            program_avg = google.visualization.arrayToDataTable(stats_data.TN_AVG)
        }
        else if (zone=='Outside Tamilnadu'){
            ie_data = google.visualization.arrayToDataTable(stats_data.OTN_IE_PROGRAMS)
            other_prg_data = google.visualization.arrayToDataTable(stats_data.OTN_OTHER_PROGRAMS)
            program_avg = google.visualization.arrayToDataTable(stats_data.OTN_AVG)
        }
         else if (zone=='Isha Yoga Center'){
            ie_data = google.visualization.arrayToDataTable(stats_data.IYC_IE_PROGRAMS)
            other_prg_data = google.visualization.arrayToDataTable(stats_data.IYC_OTHER_PROGRAMS)
            program_avg = google.visualization.arrayToDataTable(stats_data.IYC_AVG)
        }
        else if (zone=='Overseas'){
            ie_data = google.visualization.arrayToDataTable(stats_data.OVS_IE_PROGRAMS)
            other_prg_data = google.visualization.arrayToDataTable(stats_data.OVS_OTHER_PROGRAMS)
            program_avg = google.visualization.arrayToDataTable(stats_data.OVS_AVG)
        }
        else if (zone=='Training'){
//            ie_data = google.visualization.arrayToDataTable(stats_data.TRAINING)
//            other_prg_data = google.visualization.arrayToDataTable(stats_data.TRAINING)
//            program_avg = google.visualization.arrayToDataTable(stats_data.TRAINING)
            $("#row-tn-other-table").hide()
            $("#row-tn-ie-table").hide()
            $("#row-tn-other-chart").hide()
            $("#row-tn-ie-chart").hide()
            $("#row-tn-class-average").hide()
        }
        else if (zone=='Uyir Nokkam'){
            ie_data = google.visualization.arrayToDataTable(stats_data.TN_UN)
            program_avg = google.visualization.arrayToDataTable(stats_data.TN_UN_AVG)
            $("#header_ie_chart").text('Number of participants')
            $("#header_ie_table").text('Number of participants')
            $("#header_other_table").text('No of classes')
            $("#header_other_chart").text('No of classes')
            if(isChart){
                $("#row-tn-other-table").hide()
                $("#row-tn-ie-table").hide()
                $("#row-tn-other-chart").hide()
                $("#row-tn-ie-chart").show()
                $("#row-tn-class-average").show()
                $("#container2").hide()
                $("#container4").show()
            }
            else{
                $("#row-tn-other-table").show()
                $("#row-tn-ie-table").show()
                $("#row-tn-other-chart").hide()
                $("#row-tn-ie-chart").hide()
                $("#row-tn-class-average").hide()
                $("#container2").show()
                $("#container4").hide()
            }
        }
        if (zone=='Tamil Nadu' || zone=='Outside Tamilnadu' || zone=='Overseas' || zone=='Isha Yoga Center'){
            $("#header_ie_chart").text('Number of participants - Inner Engineering & Isha Yoga Program')
            $("#header_ie_table").text('Number of participants - Inner Engineering & Isha Yoga Program')
            $("#header_other_table").text('Number of participants - Other programs')
            $("#header_other_chart").text('Number of participants - Other programs')
            $("#container2").show()
            if(isChart){
                $("#row-tn-other-table").hide()
                $("#row-tn-ie-table").hide()
                $("#row-tn-other-chart").show()
                $("#row-tn-ie-chart").show()
                $("#row-tn-class-average").show()
                $("#container4").show()
                }
            else{
                $("#row-tn-other-table").show()
                $("#row-tn-ie-table").show()
                $("#row-tn-other-chart").hide()
                $("#row-tn-ie-chart").hide()
                $("#row-tn-class-average").hide()
                $("#container4").hide()
            }
         }
        var ie_data_view = new google.visualization.DataView(ie_data);
        setColumnDataValue(ie_data_view, zone)

        var chart_div = document.getElementById('tn-ie-chart');
        var chart = new google.visualization.ComboChart(chart_div);
          // Wait for the chart to finish drawing before calling the getImageURI() method.
          google.visualization.events.addListener(chart, 'ready', function () {
            chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
          });
        chart.draw(ie_data_view, options);


        if (zone=='Tamil Nadu' || zone=='Outside Tamilnadu' || zone=='Overseas' || zone=='Isha Yoga Center'){
            var chart_other_div = document.getElementById('tn-other-chart');
            var chart_other = new google.visualization.ComboChart(chart_other_div);
            // Wait for the chart to finish drawing before calling the getImageURI() method.
            google.visualization.events.addListener(chart_other, 'ready', function () {
                chart_other_div.innerHTML = '<img src="' + chart_other.getImageURI() + '">';
              });
            var other_prg_data_view = new google.visualization.DataView(other_prg_data);
            setColumnDataValue(other_prg_data_view, zone)
            chart_other.draw(other_prg_data_view, options);
        }

        var table = new google.visualization.Table(document.getElementById('tn-ie-table'));
        table.draw(ie_data, {showRowNumber: true, width: '100%', height: '100%'});
        var table = new google.visualization.Table(document.getElementById('tn-other-table'));
        table.draw(other_prg_data, {showRowNumber: true, width: '100%', height: '100%'});

        var chart_average_div = document.getElementById('tn-class-average');
        var chart_average = new google.visualization.ComboChart(chart_average_div);
        // Wait for the chart to finish drawing before calling the getImageURI() method.
        google.visualization.events.addListener(chart_average, 'ready', function () {
            chart_average_div.innerHTML = '<img src="' + chart_average.getImageURI() + '">';
          });
        var average_data_view = new google.visualization.DataView(program_avg);
        setColumnDataValue(average_data_view, zone)
        chart_average.draw(average_data_view, options);
        var table = new google.visualization.Table(document.getElementById('tn-other-table'));
        table.draw(program_avg, {showRowNumber: true, width: '100%', height: '100%'});
    }

    function setColumnDataValue(data_view, zone){
         if (zone=='Tamil Nadu' || zone=='Outside Tamilnadu' || zone=='Overseas' || zone=='Uyir Nokkam') {
                data_view.setColumns([0, 1,{ calc: "stringify",
                         sourceColumn: 1,
                         type: "string",
                         role: "annotation" },
                         2,{ calc: "stringify",
                         sourceColumn: 2,
                         type: "string",
                         role: "annotation" },
                         3, { calc: "stringify",
                         sourceColumn: 3,
                         type: "string",
                         role: "annotation" },
                         4, { calc: "stringify",
                         sourceColumn: 4,
                         type: "string",
                         role: "annotation" },
                         5, { calc: "stringify",
                         sourceColumn: 5,
                         type: "string",
                         role: "annotation" },
                         6, { calc: "stringify",
                         sourceColumn: 6,
                         type: "string",
                         role: "annotation" },
                       ]);
        }
        else{
            data_view.setColumns([0, 1,{ calc: "stringify",
                         sourceColumn: 1,
                         type: "string",
                         role: "annotation" },
                         2,{ calc: "stringify",
                         sourceColumn: 2,
                         type: "string",
                         role: "annotation" },
                       ]);
        }
    }
})(jQuery);