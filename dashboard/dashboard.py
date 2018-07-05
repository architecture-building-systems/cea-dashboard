from flask import Flask
from importlib import import_module

import cea.config
import cea.plots

import yaml
import os


def list_tools():
    """List the tools known to the CEA. The result is grouped by category.
    """
    import cea.scripts
    from itertools import groupby

    tools = sorted(cea.scripts.for_interface('dashboard'), key=lambda t: t.category)
    result = {}
    for category, group in groupby(tools, lambda t: t.category):
        result[category] = [t for t in group]
    return result


def load_plots_data():
    plots_yml = os.path.join(os.path.dirname(cea.plots.__file__), 'plots.yml')
    return yaml.load(open(plots_yml).read())


def main(config):
    app = Flask(__name__, static_folder='base/static')
    app.config.from_mapping({'DEBUG': True,
                             'SECRET_KEY': 'secret'})

    # provide the list of tools
    @app.context_processor
    def tools_processor():
        return dict(tools=list_tools())

    @app.context_processor
    def plots_processor():
        plots_data = load_plots_data()
        plots_categories = set([plot['category'] for plot in plots_data.values()])
        return dict(plots_data=plots_data, plots_categories=plots_categories)

    import base.routes
    import tools.routes
    import plots.routes
    import inputs.routes
    import project.routes

    app.register_blueprint(base.routes.blueprint)
    app.register_blueprint(tools.routes.blueprint)
    app.register_blueprint(plots.routes.blueprint)
    app.register_blueprint(inputs.routes.blueprint)
    app.register_blueprint(project.routes.blueprint)

    # keep a copy of the configuration we're using
    app.cea_config = config
    app.plots_data = load_plots_data()

    # keep a list of running scripts - (Process, Connection)
    # the protocol for the Connection messages is tuples ('stdout'|'stderr', str)
    app.workers = {}  # script-name -> (Process, Connection)

    app.run(host='localhost', port=5050, threaded=False)


if __name__ == '__main__':
    main(cea.config.Configuration())