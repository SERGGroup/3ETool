from EEETools.Tools.API.Tools.main_tools import get_result_data_frames, update_exergy_values, get_debug_data_frames
from EEETools.Tools.API.Tools.sankey_diagram_generation import SankeyDiagramGenerator, SankeyDiagramOptions
from EEETools.Tools.EconomicModel.PECHandlerModels.ModulesHandlers import EconomicModulesHandler
from EEETools.Tools.API.ExcelAPI.modules_importer import export_solution_to_excel
from flask import json, jsonify, Flask, request, send_from_directory, redirect, abort
from EEETools.MainModules.main_module import CalculationOptions
from EEETools.MainModules.main_module import ArrayHandler
from EEETools.costants import RES_DIR
from datetime import datetime
from urllib.parse import quote
from flask_cors import CORS
import multiprocessing
import typing as t
import warnings
import os
import io

CURR_DIR = os.path.join(os.path.dirname(__file__))
DOC_DIR = os.path.join(CURR_DIR, "resources")
DEBUG_DIR = os.path.join(CURR_DIR, "debug_dir")
BUILD_DIR = os.path.join(CURR_DIR, "build")
EXAMPLE_DIR = os.path.join(CURR_DIR, "example_topologies")

debug=False
economy_modules_handler = EconomicModulesHandler()

def run_drag_drop_server():

    backend_proc = multiprocessing.Process(target=run_json_backend)
    frontend_proc = multiprocessing.Process(target=run_react_frontend)

    backend_proc.start()
    frontend_proc.start()

    backend_proc.join()
    frontend_proc.join()

def run_react_frontend(host="localhost", port=8002):
    app = get_react_frontend_app()
    app.run(host=host, port=port, debug=debug)

def get_react_frontend_app():
    app = Flask(__name__, static_folder=BUILD_DIR)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    @app.route('/api/download', methods=["GET"])
    def frontend_download_file():
        return download_file()

    @app.route('/api/<path:path>', methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    def redirect_api(path):
        query_string = request.query_string.decode()
        new_url = f"http://localhost:8081/api/{path}"
        if query_string:
            new_url += f"?{query_string}"
        return redirect(new_url, code=307)

    return app

def run_json_backend(host="localhost", port=8081):
    app = get_backend_app()
    app.run(host=host, port=port, debug=debug)

def get_backend_app():
    app = Flask(__name__)
    CORS(app)
    app.add_url_rule("/api/component-types", view_func=prepare_json_list, methods=["GET"])
    app.add_url_rule("/api/analyze", view_func=analyze_post_view, methods=["POST", "GET"])
    app.add_url_rule("/api/sankey", view_func=analyze_post_view, methods=["POST", "GET"])
    app.add_url_rule("/api/sankey_cost", view_func=analyze_post_view, methods=["POST", "GET"])
    app.add_url_rule("/api/economic_models", view_func=return_economic_models_list, methods=["POST", "GET"])
    app.add_url_rule("/api/download", view_func=download_file, methods=["GET"])
    app.add_url_rule("/api/example_topology/<filename>", view_func=handle_example, methods=["GET"])
    app.add_url_rule("/api/example_topology/", view_func=handle_example, methods=["GET"])

    return app

def analyze_post_view():

    if 'file' not in request.files:
        return "No JSON file provided", 400
    file = request.files['file']
    if file.filename == '':
        return "No JSON file provided", 400
    json_content = file.read().decode("utf-8")
    json_file = io.StringIO(json_content)

    # Salva il file JSON se l'app è in modalità debug
    if debug:
        save_path = os.path.join(DEBUG_DIR, f"debug_{file.filename}")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(json_content)

    # Determina il tipo di output in base all'URL chiamata
    if request.path.endswith("/sankey"):
        # Restituisce il diagramma Sankey come HTML (bytes)
        html_buffer = __plot_sankey(io.StringIO(json_content), plot_cost=False)
        return (
            html_buffer.getvalue(),
            200,
            {
                "Content-Type": "text/html; charset=utf-8",
                "Content-Disposition": f"attachment; filename=sankey.html"
            }
        )
    elif request.path.endswith("/sankey_cost"):
        # Restituisce il diagramma Sankey con costi come HTML (bytes)
        html_buffer = __plot_sankey(io.StringIO(json_content), plot_cost=True)
        return (
            html_buffer.getvalue(),
            200,
            {
                "Content-Type": "text/html; charset=utf-8",
                "Content-Disposition": f"attachment; filename=sankey_cost.html"
            }
        )
    else:
        # Restituisce il file Excel come bytes
        result_filename, excel_bytes = calculate_json(json_file)
        return (
            excel_bytes,
            200,
            {
                "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "Content-Disposition": f"attachment; filename={result_filename}"
            }
        )

def download_file():
    filename = request.args.get('file')
    if not filename:
        abort(400, description="File parameter is required")
    file_path = os.path.join(DOC_DIR, filename)
    if not os.path.isfile(file_path):
        abort(404, description="File not found")
    return send_from_directory(DOC_DIR, filename, as_attachment=True)

def handle_example(filename=None):
    if filename is None:
        # Restituisce la lista dei file nella cartella
        files = [f for f in os.listdir(EXAMPLE_DIR) if os.path.isfile(os.path.join(EXAMPLE_DIR, f))]
        return jsonify(files)
    else:
        file_path = os.path.join(EXAMPLE_DIR, filename)
        if not os.path.isfile(file_path):
            abort(404, description="File not found")
        return send_from_directory(EXAMPLE_DIR, filename, as_attachment=True)

def return_economic_models_list():

    return jsonify(economy_modules_handler.get_json_inputs_dict())

def prepare_json_list():
    array_handler = ArrayHandler()
    return jsonify(array_handler.get_json_component_description())

def calculate_json(json_in: t.IO[t.AnyStr]):

    array_handler = import_json_input(json_in)
    array_handler.calculate()

    excel_bytes = export_solution_to_excel("debug_dir/results.xlsx", array_handler, return_bytes=True)
    return "results.xlsx", excel_bytes

def import_json_input(json_in: t.IO[t.AnyStr]) -> ArrayHandler:

    topology = json.load(json_in)

    with warnings.catch_warnings():

        warnings.simplefilter("ignore")

        array_handler = ArrayHandler()
        array_handler.options = __get_options_from_topology(topology)
        economic_model = economy_modules_handler.init_subclass(topology)

        # import connections
        json_connection_data = topology.get('edges', [])

        for conn in json_connection_data:

            new_conn = array_handler.append_connection()

            new_conn.index = float(conn["label"])
            new_conn.name = conn["data"]["name_txt"]
            new_conn.exergy_value = float(conn["data"]["exergy"])

        # import blocks
        json_block_data = topology.get('nodes', [])

        for block in json_block_data:

            block_data = block.get('data', {})
            block_type = block_data["type"]
            block_index = float(block.get('id', -1))
            block_cost = float(block_data.get("cost", 0))

            if block_index is not None:
                in_conn, out_conn = __identify_json_connections(block_index, json_connection_data)

            if block_type == "System Input" and not block_cost == 0:
                for conn in out_conn.get('fuel input', []):
                    new_conn = array_handler.find_connection_by_index(float(conn["label"]))
                    if new_conn:
                        new_conn.rel_cost = block_cost / 3600 # from €/kWh to €/kJ

            elif block_type == "Useful Effect":
                for conn in in_conn.get('useful effect', []):
                    new_conn = array_handler.find_connection_by_index(float(conn["label"]))
                    if new_conn:
                        new_conn.is_useful_effect = True

            elif block_type not in ["System Input", "Useful Effect", "Losses"]:
                new_block = array_handler.append_block(block_type)
                new_block.index = block_index
                new_block.name = block_data["label"]
                new_block.comp_cost = economic_model.get_cost(block_cost)
                new_block.append_json_connection(in_conn, out_conn)

        return array_handler

def __get_options_from_topology(topology) -> CalculationOptions:

    calculation_option = CalculationOptions()
    options = topology.get('options', None)

    if options is not None:
        calculation_type = options.get('analysis_type', 'exergo-economic')
        topology_options = options.get('calculation_options', None)

    calculation_option.is_exergo_economic_analysis = (calculation_type == 'exergo-economic')

    if topology_options is not None:
        calculation_option.calculate_on_pf_diagram = topology_options.get('calculate_on_pf_diagram', True)
        calculation_option.valve_is_dissipative = topology_options.get('valve_is_dissipative', True)
        calculation_option.condenser_is_dissipative = topology_options.get('condenser_is_dissipative', True)
        calculation_option.loss_cost_is_zero = topology_options.get('loss_cost_is_zero', True)

    return calculation_option

def __identify_json_connections(block_index: int, input_list: dict):

    # This method is used to find the connection in the JSON input and append it to the block
    # It is used in the append_json_strings method

    in_json_conn = dict()
    out_json_conn = dict()

    for conn in input_list:

        if float(conn.get("source", -1)) == block_index:
            handle_name = conn.get('sourceHandle', "None")
            if handle_name not in out_json_conn.keys():
                out_json_conn.update({handle_name: []})

            out_json_conn[handle_name].append(conn)

        if float(conn.get("target", -1)) == block_index:
            handle_name = conn.get('targetHandle', "None")
            if handle_name not in in_json_conn.keys():
                in_json_conn.update({handle_name: []})

            in_json_conn[handle_name].append(conn)

    return in_json_conn, out_json_conn

def __plot_sankey( json_in: t.IO[t.AnyStr], plot_cost = False):

    array_handler = import_json_input(json_in)

    options = SankeyDiagramOptions()
    options.generate_on_pf_diagram = True
    options.display_costs = plot_cost

    return SankeyDiagramGenerator(array_handler, options).show(export_html=True)


if __name__ == '__main__':

    run_drag_drop_server()
