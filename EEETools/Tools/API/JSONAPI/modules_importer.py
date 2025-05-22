from EEETools.Tools.API.Tools.main_tools import get_result_data_frames, update_exergy_values, get_debug_data_frames
from EEETools.Tools.API.Tools.sankey_diagram_generation import SankeyDiagramGenerator, SankeyDiagramOptions
from EEETools.Tools.API.ExcelAPI.modules_importer import export_solution_to_excel
from EEETools.MainModules.main_module import CalculationOptions
from EEETools.MainModules.main_module import ArrayHandler
from flask import json, jsonify, Flask, request
from datetime import datetime
from flask_cors import CORS
import typing as t
import warnings
import os
import io

CURRENT_DIR = os.path.join(os.path.dirname(__file__), "debug_dir")
debug=False

def run_json_backend(host="localhost", port=8081):
    app = Flask(__name__)
    CORS(app)
    app.add_url_rule("/api/component-types", view_func=prepare_json_list, methods=["GET"])
    app.add_url_rule("/analyze", view_func=analyze_post_view, methods=["POST", "GET"])
    app.add_url_rule("/sankey", view_func=analyze_post_view, methods=["POST", "GET"])
    app.add_url_rule("/sankey_cost", view_func=analyze_post_view, methods=["POST", "GET"])
    app.run(host=host, port=port, debug=debug)

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
        save_path = os.path.join(CURRENT_DIR, f"debug_{file.filename}")
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
        calculation_option = CalculationOptions()
        array_handler.options = calculation_option

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
                        new_conn.rel_cost = block_cost

            elif block_type == "Useful Effect":
                for conn in in_conn.get('useful effect', []):
                    new_conn = array_handler.find_connection_by_index(float(conn["label"]))
                    if new_conn:
                        new_conn.is_useful_effect = True

            elif block_type not in ["System Input", "Useful Effect", "Losses"]:
                new_block = array_handler.append_block(block_type)
                new_block.index = block_index
                new_block.name = block_data["label"]
                new_block.comp_cost = block_cost
                new_block.append_json_connection(in_conn, out_conn)

        return array_handler

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

    run_json_backend(host="localhost", port=8081)
