import inspect

called_from_setup = False
for frame in inspect.stack():

    if "setup.py" in frame.filename:

        called_from_setup = True
        break

if not called_from_setup:

    from EEETools.Tools.API.terminal_api import paste_default_excel_file, paste_components_documentation, paste_user_manual
    from EEETools.Tools.API.terminal_api import calculate, launch_connection_debug, launch_network_display