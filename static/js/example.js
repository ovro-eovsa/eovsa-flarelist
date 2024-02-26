document.addEventListener('DOMContentLoaded', function() {
    // Initialize flatpickr for datetime pickers
    flatpickr(document.querySelectorAll('.datetime-picker'), {
        enableTime: true,
        dateFormat: "Y-m-d\\TH:i:S",
        defaultHour: 0,
        altFormat: "Y-m-d\\TH:i:S",
        allowInput: true,
        time_24hr: true,
    });

    var baseUrl = isOvsa ? '/flarelist' : '';

    // Function to render table with data
    function renderTable(data) {
        let tableBody = '';
        data.forEach((item) => {
            let row = '<tr>';
            ['_id'].forEach((key) => {
                row += '<td>' + (item[key] || '') + '</td>';
            }); // Handle null values
            // Add a cell for the flare_id with an onclick event
            row += '<td><a href="#" class="flare-id-link" data-flare-id="' + item['flare_id'] + '">' + item['flare_id'] + '</a></td>';

            ['start', 'peak', 'end', 'GOES_class', 'link_dspec', 'link_dspec_data', 'link_movie', 'link_fits'].forEach((key) => {
                row += '<td>' + (item[key] || '') + '</td>'; // Handle null values
            });

            row += '</tr>';
            tableBody += row; // Append the row to the tableBody
        });

        // Show the table and update its content
        $('#flare-list').show();
        $('#flare-list > tbody').html(tableBody);

        attachFlareIdClickEvent()
        // // Add click event listeners to the flare_id links
        // $('.flare-id-link').on('click', function(e) {
        //     e.preventDefault(); // Prevent the default anchor action
        //     var flareId = $(this).data('flare-id');
        //     fetchAndDisplayFlareData(flareId);
        // });
    }

    // Function to attach click events to flare_id links
    function attachFlareIdClickEvent() {
        $('.flare-id-link').on('click', function(e) {
            e.preventDefault(); // Prevent the default anchor action
            var flareId = $(this).data('flare-id');
            fetchAndDisplayFlareData(flareId);
        });
    }


    function fetchAndDisplayFlareData(flareId) {
        $.ajax({
            url: baseUrl + `/fetch-spectral-data/${flareId}`,
            method: 'GET',
            success: function(response) {
                var plotData = JSON.parse(response.plot_data_ID);

                var config = {
                    modeBarButtonsToAdd: [{
                        name: 'Toggle Log-Y Scale',
                        // icon: {
                        //     path: '/data1/xychen/flaskenv/minisdc/static/images/icon-logY.svg',
                        //     transform: 'scale(1.5)'
                        // },
                        icon: Plotly.Icons.pencil,
                        click: function(gd) {
                            var currentType = gd.layout.yaxis.type;
                            var newType = currentType === 'log' ? 'linear' : 'log';
                            Plotly.relayout(gd, 'yaxis.type', newType);
                        }
                    }],
                    displaylogo: false,
                    responsive: true
                };

                // Use the config object here to include the custom button
                Plotly.newPlot('plot-container', plotData.data, plotData.layout, config);
            },
            error: function(xhr, status, error) {
                console.error("Failed to fetch data for Flare ID:", flareId, status, error);
            }
        });
    }


    // Function to fetch data based on given start and end dates
    function fetchData(start, end) {
        $.ajax({
            url: baseUrl + '/api/flare/query',
            type: "POST",
            data: { 'start': start, 'end': end },
            dataType: "json",
            success: function(response) {
                if (response.error) {
                    console.error(response.error);
                } else {
                    renderTable(response.result);
                    attachFlareIdClickEvent()
                }
            },
            error: function(xhr, status, error) {
                console.error("Error occurred: " + error);
                showError("An error occurred while processing your request.");
            }
        });
    }

    // On query button click, fetch data for the given date range
    $('#query-btn').on('click', function(e) {
        e.preventDefault();
        let start = $('#start').val();
        let end = $('#end').val();
        fetchData(start, end);
    });


    // Automatically fetch data for the last month on page load
    (function autoFetchDataForLastMonth() {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setMonth(startDate.getMonth() - 1);

        // Format dates to YYYY-MM-DD format
        const start = startDate.toISOString().split('T')[0];
        const end = endDate.toISOString().split('T')[0];

        // Fetch data without needing to click the query button
        fetchData(start, end);
    })();
});

