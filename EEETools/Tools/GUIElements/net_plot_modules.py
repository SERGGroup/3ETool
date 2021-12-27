from EEETools.MainModules.main_module import ArrayHandler
from pyvis.network import Network


def display_network(array_handler: ArrayHandler):

    network = Network(height='750px', width='100%', bgcolor='#222222', font_color='white')
    network.barnes_hut()

    for block in array_handler.block_list:

        if not block.is_support_block:

            network.add_node(block.ID, label="{} - {}".format(block.ID, block.name))

    for conn in array_handler.connection_list:

        if not conn.is_system_input and not conn.is_system_output and not conn.is_internal_stream:

            from_block_ID = conn.from_block.get_main_ID
            to_block_ID = conn.to_block.get_main_ID

            network.add_edge(from_block_ID, to_block_ID)

    network.show('topology.html')