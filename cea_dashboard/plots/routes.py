from flask import Blueprint, render_template, current_app, request, abort, make_response

import cea.inputlocator
import os
import cea.plots.categories

import importlib
import plotly.offline
import json
import yaml


blueprint = Blueprint(
    'plots_blueprint',
    __name__,
    url_prefix='/plots',
    template_folder='templates',
    static_folder='static',
)


@blueprint.route('/index')
def index():
    cea_config = current_app.cea_config
    locator = cea.inputlocator.InputLocator(scenario=cea_config.scenario)
    with open(locator.get_dashboard_yml()) as dashboard_yml:
        dashboard = yaml.load(dashboard_yml)

    def load_plot_from_dashboard_yml(plot_definition):
        category_name = plot_definition['category']
        plot_id = plot_definition['plot']
        plot_class = cea.plots.categories.load_plot_by_id(category_name, plot_id)
        buildings_ = plot_definition['buildings']
        return plot_class(cea_config, locator, buildings_)
    plots = [load_plot_from_dashboard_yml(plot_definition) for plot_definition in dashboard]

    return render_template('dashboard.html', plots=plots, scenario=cea_config.scenario)


@blueprint.route('/category/<category>')
def route_category(category):
    if not cea.plots.categories.is_valid_category(category):
        return abort(404)

    cea_config = current_app.cea_config
    locator = cea.inputlocator.InputLocator(scenario=cea_config.scenario)
    buildings = cea_config.plots.buildings

    category = cea.plots.categories.load_category(category)
    plots = [plot_class(cea_config, locator, **{'buildings': buildings}) for plot_class in category.plots]
    return render_template('category.html', category=category, plots=plots)


@blueprint.route('/div/<category_name>/<plot_id>')
def route_div(category_name, plot_id):
    """Return the plot as a div to be used in an AJAX call"""
    try:
        config = current_app.cea_config
        locator = cea.inputlocator.InputLocator(config.scenario)
        buildings = config.plots.buildings

        plot_class = cea.plots.categories.load_plot_by_id(category_name, plot_id)
        if not plot_class:
            return abort(404)
        plot = plot_class(config, locator, **{'buildings': buildings})
        response = make_response(plot.plot_div(), 200)
        return response
    except Exception as ex:
        return abort(500, ex.message)


@blueprint.route('/plot/<category_name>/<plot_id>')
def route_plot(category_name, plot_id):
    plot_class = cea.plots.categories.load_plot_by_id(category_name, plot_id)
    if not plot_class:
        return abort(404)

    config = current_app.cea_config
    locator = cea.inputlocator.InputLocator(config.scenario)
    buildings = config.plots.buildings
    plot = plot_class(config, locator, **{'buildings': buildings})

    return render_template('plot.html', category_name=category_name,
                           plot=plot, parameters={'buildings': buildings,
                                                  'all_buildings': locator.get_zone_building_names()})


def get_plot_parameters(locator, plot):
    """Return a dictionary of parameters for a plot

    :param InputLocator locator: input locator for the plots
    :param str plot: name of the plot
    """
    parameters = {}
    plot_data = current_app.plots_data[plot]
    if 'buildings' in plot_data['parameters']:
        parameters['buildings'] = (current_app.cea_config.plots.buildings, locator.get_zone_building_names())
    return parameters


def get_plot_fig(locator, plot):
    plot_data = current_app.plots_data[plot]
    module_name, class_name = os.path.splitext(plot_data['preprocessor'])
    class_name = class_name[1:]
    module = importlib.import_module(module_name)

    config = current_app.cea_config
    args = {'locator': locator, 'config': config}
    if 'weather' in plot_data['parameters']:
        args['weather'] = config.weather
    if 'buildings' in plot_data['parameters']:
        valid_buildings = locator.get_zone_building_names()
        args['buildings'] = [building for building in json.loads(request.args.get('buildings', default='[]'))
                             if building in valid_buildings]
    if 'scenarios' in plot_data['parameters']:
        args['scenarios'] = config.plots.scenarios
        del args['locator']
    if 'individual' in plot_data['parameters']:
        args['individual'] = config.plots.individual
    if 'generations' in plot_data['parameters']:
        args['generations'] = config.plots.generations
    if 'network_type' in plot_data['parameters']:
        args['network_type'] = config.plots.generations
    if 'network_names' in plot_data['parameters']:
        args['network_names'] = config.plots.network_names

    preprocessor = getattr(module, class_name)(**args)
    plot_function = getattr(preprocessor, plot_data['plot-function'])
    fig = plot_function(category='dashboard')
    return fig