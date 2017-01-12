/**
 * Created by manimaran on 21-12-2016.
 */
refresh_reports = null;

(function($) {
    google.charts.load('current', {'packages':['corechart', 'table']});
    google.charts.setOnLoadCallback(drawVisualization);

    function filterRows(nestedArray, column, value, notequals) {
        filteredArray = [];

        if (notequals === undefined) {
            for (i = 0; i < nestedArray.length; i++) {
                if (nestedArray[i][column] == value) {
                    filteredArray.push(nestedArray[i]);
                }
            }

            return filteredArray;
        }

        if (notequals === true) {
            for (i = 0; i < nestedArray.length; i++) {
                if (nestedArray[i][column] != value) {
                    filteredArray.push(nestedArray[i]);
                }
            }

            return filteredArray;
        }

    }

    function refreshReports(r_zone) {
        var currentZone = document.getElementById(aasaan_stats_dashboard.report_zone).innerText;
        var clickedZone = r_zone;
        var clickedZoneName = document.getElementById(r_zone).innerText;
        if (currentZone == clickedZoneName) {
            // active zone was clicked. no action is required
            return
        }

        document.getElementById(clickedZone).parentNode.className = "active";
        document.getElementById(aasaan_stats_dashboard.report_zone).parentNode.className = "";
        aasaan_stats_dashboard.report_zone = r_zone;

        pageHeader = document.getElementsByClassName("page-header")[0];
        pageHeader.innerText = "Statistics Dashboard - " + clickedZoneName;

        drawVisualization(clickedZoneName);
    }
    refresh_reports = refreshReports;
    function drawVisualization(zone) {

        if(zone==undefined || zone=='undefined')
            zone='Tamil Nadu'

        var options = {
          title : '',
          vAxis: {title: 'Participants'},
          hAxis: {title: 'Month'},
          seriesType: 'bars',
          series: {5: {type: 'line'}},
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

        var chart = new google.visualization.ComboChart(document.getElementById('tn-ie-chart'));
        chart.draw(ie_data, options);
        var chart = new google.visualization.ComboChart(document.getElementById('tn-other-chart'));
        chart.draw(other_prg_data, options);
        var table = new google.visualization.Table(document.getElementById('tn-ie-table'));
        table.draw(ie_data, {showRowNumber: true, width: '100%', height: '100%'});
        var table = new google.visualization.Table(document.getElementById('tn-other-table'));
        table.draw(other_prg_data, {showRowNumber: true, width: '100%', height: '100%'});

        var class_average_options = {
            title : '',
            vAxis: {title: 'Classes'},
            hAxis: {title: 'Month'},
            seriesType: 'bars',
            series: {5: {type: 'line'}},
            annotations: {
                boxStyle: {
                    stroke: '#888', strokeWidth: 1, rx: 10, ry: 10,
                    gradient: {
                        color1: '#fbf6a7', color2: '#33b679',
                        x1: '0%', y1: '0%', x2: '100%', y2: '100%',
                        useObjectBoundingBoxUnits: true
                    }
                }
            },
            selectionMode: 'multiple',
            tooltip: {trigger: 'selection'},
        };

        var chart = new google.visualization.ComboChart(document.getElementById('tn-class-average'));
        chart.draw(program_avg, class_average_options);

    }
})(jQuery);