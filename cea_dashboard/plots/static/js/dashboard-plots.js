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
        let category_name = this.dataset.ceaCategory;
        let plot_id = this.dataset.ceaPlot;
        let parameters = this.dataset.ceaParameters;
        load_plot(category_name, plot_id, parameters);
    });
}

function load_plot(category_name, plot_id, parameters) {
    $.get('../div/' + category_name + '/' + plot_id, {'parameters': parameters}, function(data){
        $('#x_content-' + plot_id).replaceWith(data);
    }).fail(function(data) {
        $('#x_content-' + plot_id).children().replaceWith('ERROR: ' + $(data.responseText).filter('p').text());
        console.log('error creating plot:');
        console.log(data);
    });
}

function open_plot(cea_plot) {
    // navigate to the plot as defined in the data attributes of the cea_plot element
    let category = cea_plot.dataset.ceaCategory;
    let plot_id = cea_plot.dataset.ceaPlot;
    let parameters = cea_plot.dataset.ceaParameters;

    let url = '../plot/' + category + '/' + plot_id + '?' + $.param({'parameters': parameters}, true);
    window.location.href = url;
}