# 3ETool

__3ETool__ contains some useful tools developed by the [SERG research group](https://www.dief.unifi.it/vp-177-serg-group-english-version.html) 
of the [University of Florence](https://www.unifi.it/changelang-eng.html) for performing exergo-economic and exergo environmental analysis. The __user manual__ can be downloaded [here](https://firebasestorage.googleapis.com/v0/b/etapp-serggroup.appspot.com/o/3ETool_res%2FOther%2FUser%20Guide-eng.pdf?alt=media&token=db51ff1e-4c63-48b9-8b42-322a2eee44da). Moreover, some [youtube tutorials](https://www.youtube.com/playlist?list=PLj6A7PjCJLfa9xNOFwRc3D_XroWhKlptj) have been uploaded in order to help the user in compiling the excel file. 

### !!! NEW DRAG & DROP FUNCTIONALITY 🥳🎉!!! 
With the new drag & drop functionality, the user can simply define the topology 
using a graphical interface and then run the calculation starting from there.
to use this feature, the user has to run the following command:
```python
from EEETools import run_drag_drop_server
run_drag_drop_server()
```

This will run a server on the localhost, and the user can access it 
using the following link http://localhost:8002

### 1 - Calculation process 🤔⚙
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
Finally, once the Excel file has been compiled, the calculation can be initialized trough this command:
```python
import EEETools

EEETools.calculate()
```
calculation options and user defined excel path can be passed to the function as well (default values are _true_); in case user does not pass the path, the app will automatically open a filedialog window so that it can be selected manually
```python
import EEETools

EEETools.calculate(
    
    excel_path="your_excel_file.xlsx",
    calculate_on_pf_diagram = True, 
    loss_cost_is_zero = True, 
    valve_is_dissipative = True, 
    condenser_is_dissipative = True

)
```
### 2 - Debugging tools 👨‍💻🔍
Excel file can be debugged using some specific tools that can be launched using the following command (please select the 
Excel file that you want to debug on program request):
```python
import EEETools
EEETools.launch_connection_debug()
```
Another possible way of debugging the code is to ask the program to export the debug information on the Excel file:
```python
import EEETools
EEETools.export_debug_information()
```
Finally, topology can be displayed using:
```python
import EEETools
EEETools.launch_network_display()
```
### 3 - Sankey Diagrams 📈📊
Sankey diagram can be plotted using the following command: 
```python
import EEETools
EEETools.plot_sankey(
    
    generate_on_pf_diagram=True,
    display_costs=True,

)
```
*   ___<span style="color:#3399ff">generate_on_pf_diagram</span>___ can be omitted and 
    __is <span style="color:#3399ff">True</span> by default__:
    
    - if __False__ the connections are defined according to the __physical topology__ of the plant 
    - if __True__ the connections are based on the __product-fuel__ definition


*   ___<span style="color:#3399ff">display_costs</span>___ can be omitted and 
    __is <span style="color:#3399ff">False</span> by default__:
    
    - if __False__ the thickness of the connection in the sankey diagram is proportional to the __exergy flux__ between 
    the components (in _kW_)
    
    - if __True__ the thickness of the connection in the sankey diagram is proportional to the 
    __economic (or environmental) flux__ between the components (in _€/s_ or in _Pts/s_). In addition, for each 
    connection, the __color intensity__ is proportional to the __relative cost of the stream__ (in _€/kJ_ or in _Pts/kJ_)


### 4 - Code Structure 📁

__The application code is divided into 3 main folders:__<br/><br/>
__MainModules__ directory contains Base modules such as _Block, Connection, ArrayHandler and Drawer Classes._<br/>
__Block Sublcasses__ contains a Block subclass for each component type (e.g. expander, compressor etc.)<br/>
__Tools__ contains different APIs needed for the program to run (e.g. the cost correlation handler, 
the EES code generator, and the importer and exporter for both Excel and xml files)

### 5 - Important Information ⚠

__-------------------------- !!! THIS IS A BETA VERSION !!! --------------------------__ 

please report any bug or problems in the installation to _pietro.ungar@unifi.it_<br/>
for further information visit: https://tinyurl.com/SERG-3ETool

__-------------------------------- !!! HOW TO CITE !!! --------------------------------__ 

The following reference can be used to cite the tool in publications:
 
    Fiaschi, D., Manfrida, G., Ungar, P., Talluri, L. 
    
    Development of an exergo-economic and exergo-environmental tool for power plant assessment: 
    evaluation of a geothermal case study.
    
    https://doi.org/10.52202/062738-0003

