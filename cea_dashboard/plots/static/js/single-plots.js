$(document).ready(function() {
    load_plot();
});

function load_plot() {
    $('.cea-plot').map(function() {
        var category_name = this.dataset.ceaCategory;
        var plot_id = this.dataset.ceaPlot;
        buildings = $('#parameters-buildings').val();
        if (buildings === null) {
            buildings = [];
        }
        $.get('../../div/' + category_name + '/' + plot_id, {'buildings': JSON.stringify(buildings)}, function(data){
                $('#x_content-' + plot_id).children().replaceWith(data);
        }).fail(function(data) {
            $('#x_content-' + plot_id).children().replaceWith('ERROR: ' + $(data.responseText).filter('p').text());
            console.log('error creating plot:');
            console.log(data);
        });
    });
}

$('#parameters-buildings').on('changed.bs.select', function (e) {
  load_plot();
});