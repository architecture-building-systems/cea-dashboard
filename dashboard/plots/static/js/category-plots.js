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
        var category_name = this.dataset.ceaCategory;
        var plot_name = this.dataset.ceaPlot;
        load_plot(category_name, plot_name);
    });
}

function load_plot(category_name, plot_name) {
    $.get('../div/' + category_name + '/' + plot_name, function(data){
            $('#x_content-' + plot_name).replaceWith(data);
    });
}