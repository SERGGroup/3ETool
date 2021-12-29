import os

# RUN MODE
RUN_MODE = "administrator"
# RUN_MODE = "standard"

# ROOT DIRECTORIES
ROOT_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir)))
RES_DIR = os.path.join(ROOT_DIR, "3ETool_res")
TEST_RES_DIR = os.path.join(RES_DIR, "testResources")

if not os.path.isdir(RES_DIR):

    os.mkdir(RES_DIR)
    os.mkdir(os.path.join(RES_DIR, "ButtonIcons"))
    os.mkdir(os.path.join(RES_DIR, "EES Code Data"))
    os.mkdir(os.path.join(RES_DIR, "Images"))
    os.mkdir(os.path.join(RES_DIR, "Other"))
    os.mkdir(os.path.join(RES_DIR, "testResources"))

# FIREBASE CONFIGURATION DICT
FIREBASE_CONFIG = {

    "apiKey": "AIzaSyBQ4ZKw45o3U06gz9u1pmLd53cImzYGHj8",
    "databaseURL":"https://etapp-serggroup-default-rtdb.europe-west1.firebasedatabase.app",
    "authDomain": "etapp-serggroup.firebaseapp.com",
    "projectId": "etapp-serggroup",
    "storageBucket": "etapp-serggroup.appspot.com",
    "messagingSenderId": "12706429785",
    "appId": "1:12706429785:web:66cd6f6b1c1ed13b9e2a48",
    "measurementId": "G-T2SHVKSR9H"

}

GITHUB_CONGIF ={

    "repo": "3ETool",
    "token": "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",
    "path": "3ETool_res/Other/"

}

# EES FORMAT STYLES
STYLES = {"error": {"color": "#ff4d00",
                    "font-weight": "bold",
                    "font-style": "normal",
                    "text-decoration": "none"},

          "comments": {"color": "#8C8C8C",
                       "font-weight": "bold",
                       "font-style": "italic",
                       "text-decoration": "none"},

          "variable": {"color": "#0033B3",
                       "font-weight": "bold",
                       "font-style": "normal",
                       "text-decoration": "none"},

          "repeated_keyword": {"color": "#008080",
                               "font-weight": "bold",
                               "font-style": "normal",
                               "text-decoration": "none"},

          "known_keyword": {"color": "#008080",
                            "font-weight": "bold",
                            "font-style": "normal",
                            "text-decoration": "none"},

          "unknown_function": {"color": "#94558D",
                               "font-weight": "bold",
                               "font-style": "italic",
                               "text-decoration": "underline"},

          "known_function": {"color": "#94558D",
                             "font-weight": "bold",
                             "font-style": "normal",
                             "text-decoration": "none"},

          "default": {"color": "#000000",
                      "font-weight": "bold",
                      "font-style": "normal",
                      "text-decoration": "none"}

          }

EES_CODE_FONT_FAMILY = "Courier New"

def get_html_string(key, text):

    if not key in STYLES.keys():
        key = "default"

    style = STYLES[key]

    __html_text = '<span style="'

    __html_text += "color:" + style["color"] + "; "
    __html_text += "font-weight:" + style["font-weight"] + '; '
    __html_text += "font-style:" + style["font-style"] + '; '
    __html_text += "text-decoration:" + style["text-decoration"] + '"'

    __html_text += '>' + text + '</span>'

    return __html_text

# ZONE TYPES
ZONE_TYPE_FLUID = "fluid"
ZONE_TYPE_FLOW_RATE = "flow rate"
ZONE_TYPE_PRESSURE = "pressure"
ZONE_TYPE_ENERGY = "energy"

ZONES = [ZONE_TYPE_ENERGY, ZONE_TYPE_PRESSURE, ZONE_TYPE_FLUID, ZONE_TYPE_FLOW_RATE]