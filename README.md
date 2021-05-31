# 3ETool

__3ETool__ contains some useful tools developed by the [SERG research group](https://www.dief.unifi.it/vp-177-serg-group-english-version.html) 
of the [University of Florence](https://www.unifi.it/changelang-eng.html) for performing exergo-economic and exergo environmental analysis.

you can dawnload the beta version using __PIP__:

```
pip install 3ETools
```
Once the installation has been completed you can import the tool:
```python
import EEETool
```
and then pasting the user manual:
```python
EEETools.paste_user_manual()
```
the components documentation
```python
EEETools.paste_components_documentation()
```
and the default excel file
```python
EEETools.paste_default_excel_file()
```
to a desired path.<br/><br/>
Finally, once the excel file has been compiled, the calculation can be initialized trough the command:
```python
EEETools.calculate()
```
<br/><br/>
__The application code is divided into 3 main folders:__<br/><br/>
__MainModules__ directory contains Base modules such as _Block, Connection, ArrayHandler and Drawer Classes._<br/>
__Block Sublcasses__ contains a Block subclass for each component type (e.g. expander, compressor etc.)<br/>
__Tools__ contains different APIs needed for the program to run (e.g. the cost correlation handler, 
the EES code generator, and the importer and exporter for both Excel and xml files)

__-------------------------- !!! THIS IS A BETA VERSION !!! --------------------------__ 

please report any bug or problems in the installation to _pietro.ungar@unifi.it_<br/>
for further information visit: https://www.dief.unifi.it/vp-473-exergo-economic-analysis-software.html
