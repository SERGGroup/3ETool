# 3ETool

__3ETool__ contains some useful tools developed by the [SERG research group](https://www.dief.unifi.it/vp-177-serg-group-english-version.html) 
of the [University of Florence](https://www.unifi.it/changelang-eng.html) for performing exergo-economic and exergo environmental analysis. The __user manual__ can be downloaded [here](https://firebasestorage.googleapis.com/v0/b/etapp-serggroup.appspot.com/o/3ETool_res%2FOther%2FUser%20Guide-eng.pdf?alt=media&token=db51ff1e-4c63-48b9-8b42-322a2eee44da). Moreover, some [youtube tutorials](https://www.youtube.com/playlist?list=PLj6A7PjCJLfa9xNOFwRc3D_XroWhKlptj) have been uploaded in order to help the user in compiling the excel file.

The beta version can be downloaded using __PIP__:

```
pip install 3ETool
```
Once the installation has been completed the user can import the tool, and paste to a desired location the __user manual__, the __components documentation__ or the __default excel file__, as in the _matlab version_ of the app.
```python
import EEETools

EEETools.paste_user_manual()
EEETools.paste_components_documentation()
EEETools.paste_default_excel_file()
```
Finally, once the excel file has been compiled, the calculation can be initialized trough this command:
```python
EEETools.calculate()
```
calculation options and user defined excel path can be passed to the function as well (default values are _true_); in case user does not pass the path, the app will automatically open a filedialog window so that it can be selected manually
```python
EEETools.calculate(excel_path="your_excel_file.xlsx"
                   calculate_on_pf_diagram = True, 
                   loss_cost_is_zero = True, 
                   valve_is_dissipative = True, 
                   condenser_is_dissipative = True)
```
Excel file can be debugged using a specific tool that can be launched using the following command (please select the 
excel file that you want to debug on program request):
```python
import EEETools
EEETools.launch_connection_debug()
```
<br/><br/>
__The application code is divided into 3 main folders:__<br/><br/>
__MainModules__ directory contains Base modules such as _Block, Connection, ArrayHandler and Drawer Classes._<br/>
__Block Sublcasses__ contains a Block subclass for each component type (e.g. expander, compressor etc.)<br/>
__Tools__ contains different APIs needed for the program to run (e.g. the cost correlation handler, 
the EES code generator, and the importer and exporter for both Excel and xml files)

__-------------------------- !!! THIS IS A BETA VERSION !!! --------------------------__ 

please report any bug or problems in the installation to _pietro.ungar@unifi.it_<br/>
for further information visit: https://tinyurl.com/SERG-3ETool
