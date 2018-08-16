from flask import Blueprint, render_template, current_app, jsonify, request
from . import worker

import cea.scripts
import os

blueprint = Blueprint(
    'tools_blueprint',
    __name__,
    url_prefix='/tools',
    template_folder='templates',
    static_folder='static',
)


@blueprint.route('/index')
def index():
    return render_template('index.html')


@blueprint.route('/start/<script>', methods=['POST'])
def route_start(script):
    """Start a subprocess for the script. Store output in a queue - reference the queue by id. Return queue id.
    (this can be the process id)"""
    kwargs = {}
    print('/start/%s' % script)
    for parameter in parameters_for_script(script, current_app.cea_config):
        print('%s: %s' % (parameter.name, request.form.get(parameter.name)))
        kwargs[parameter.name] = parameter.decode(request.form.get(parameter.name))
    current_app.workers[script] = worker.main(script, **kwargs)
    return jsonify(script)


@blueprint.route('/echo', methods=['POST'])
def route_echo():
    """echo back the parameters"""
    data = request.form
    print(data)
    return jsonify(data)


@blueprint.route('/kill/<script>')
def route_kill(script):
    if not script in current_app.workers:
        return jsonify(False)
    worker, connection = current_app.workers[script]
    worker.terminate()
    return jsonify(True)


@blueprint.route('/exitcode/<script>')
def route_exitcode(script):
    if not script in current_app.workers:
        return jsonify(None)
    worker, connection = current_app.workers[script]
    return jsonify(worker.exitcode)


@blueprint.route('/is-alive/<script>')
def is_alive(script):
    if not script in current_app.workers:
        return jsonify(False)
    worker, connection = current_app.workers[script]
    return jsonify(worker.is_alive())


@blueprint.route('/read/<script>')
def read(script):
    """Reads the next message as a json dict {stream: stdout|stdin, message: str}"""
    if not script in current_app.workers:
        return jsonify(None)
    worker, connection = current_app.workers[script]
    try:
        stream, message = connection.recv()
    except EOFError:
        return jsonify(None)
    return jsonify(dict(stream=stream, message=message))


@blueprint.route('/open-file-dialog/<fqname>')
def route_open_file_dialog(fqname):
    """Return html of file/folder structure for that parameter"""

    # these arguments are only set when called with the `navigate_to` function on an already open
    # file dialog
    current_folder = request.args.get('current_folder')
    folder = request.args.get('folder')

    config = current_app.cea_config
    section, parameter_name = fqname.split(':')
    parameter = config.sections[section].parameters[parameter_name]

    if not current_folder:
        # first time calling, use current value of parameter for current folder
        current_folder = os.path.dirname(parameter.get())
        folder = None
    else:
        current_folder = os.path.abspath(os.path.join(current_folder, folder))

    print('route_open_file_dialog: current_folder=%(current_folder)s' % locals())

    folders = []
    files = []
    for entry in os.listdir(current_folder):
        if os.path.isdir(os.path.join(current_folder, entry)):
            folders.append(entry)
        else:
            ext = os.path.splitext(entry)[1]
            if parameter._extensions and ext and ext[1:] in parameter._extensions:
                files.append(entry)
            elif not parameter._extensions:
                # any file can be added
                files.append(entry)

    breadcrumbs = os.path.normpath(current_folder).split(os.path.sep)

    return render_template('file_listing.html', current_folder=current_folder,
                           folders=folders, files=files, title=parameter.help, fqname=fqname,
                           parameter_name=parameter.name, breadcrumbs=breadcrumbs)


@blueprint.route('/<script_name>')
def route_tool(script_name):
    config = current_app.cea_config
    script = cea.scripts.by_name(script_name)
    return render_template('tool.html', script=script, parameters=parameters_for_script(script_name, config))


def parameters_for_script(script, config):
    """Return a list consisting of :py:class:`cea.config.Parameter` objects for each parameter of a script"""
    import cea.interfaces.cli.cli
    cli_config = cea.interfaces.cli.cli.get_cli_config()
    parameters = [p for s, p in config.matching_parameters(cli_config.get('config', script).split())]
    return parameters