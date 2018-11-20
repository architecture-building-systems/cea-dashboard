/* get list of plots to work on... */

$(document).ready(function() {
    load_all_plots();
});


$(document).resize(function() {
    console.log('resizing!');
    load_all_plots();
});

function load_all_plots() {
    $('.cea-plot').map(function() {
        let dashboard_index = this.dataset.ceaDashboardIndex;
        let plot_index = this.dataset.ceaPlotIndex;
        let x_content_id = '#x_content-' + dashboard_index + '-' + plot_index;

        $.get('../div/' + dashboard_index + '/' + plot_index, function(data){
                $(x_content_id).children().replaceWith(data);
        }).fail(function(data) {
            $(x_content_id).children().replaceWith('ERROR: ' + $(data.responseText).filter('p').text());
            console.log('error creating plot:');
            console.log(data);
        });
    });
}

function cea_rename_dashboard() {

}