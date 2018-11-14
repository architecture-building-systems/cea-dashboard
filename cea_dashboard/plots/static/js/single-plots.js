$(document).ready(function() {
    load_plot();
});

function load_plot() {
    $('.cea-plot').map(function() {
        let category_name = this.dataset.ceaCategory;
        let plot_id = this.dataset.ceaPlot;
        let parameters = this.dataset.ceaParameters;

        $.get('../../div/' + category_name + '/' + plot_id, {'parameters': parameters}, function(data){
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