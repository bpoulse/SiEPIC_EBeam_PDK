import pya

#Define different technologies, their layers and library names
#DBU is defined dynamically from tech layer file (done in load_technology)
TECHNOLOGIES = {
  'GSiP': {
    'name' : 'GSiP',
    'library': 'GSiP',
    'LayerSi' : pya.LayerInfo(1, 0),
    'LayerSiEtch1' : pya.LayerInfo(2, 0),
    'LayerSiEtch2' : pya.LayerInfo(3, 0),
    'LayerGe': pya.LayerInfo(5, 0),
    'LayerOxEtch': pya.LayerInfo(6, 0),
    'LayerDeepTrench': pya.LayerInfo(7, 0),
    'LayerSiN': pya.LayerInfo(20, 0),
    'LayerSiP': pya.LayerInfo(21, 0),
    'LayerSiN+': pya.LayerInfo(22, 0),
    'LayerSiP+': pya.LayerInfo(23, 0),
    'LayerSiN++': pya.LayerInfo(24, 0),
    'LayerSiP++': pya.LayerInfo(25, 0),
    'LayerGeN++': pya.LayerInfo(20, 0),
    'LayerGeP+': pya.LayerInfo(21, 0),
    'LayerVC': pya.LayerInfo(40, 0),
    'LayerM1': pya.LayerInfo(41, 0),
    'LayerVL': pya.LayerInfo(44, 0),
    'LayerML': pya.LayerInfo(45, 0),
    'LayerMLOpen': pya.LayerInfo(46, 0),
    'LayerMHeater': pya.LayerInfo(47, 0),
    'LayerM1KO': pya.LayerInfo(60, 0),
    'LayerSiKO': pya.LayerInfo(63, 0),
    'LayerText' : pya.LayerInfo(66, 0),
    'LayerDRCexclude': pya.LayerInfo(67, 0),
    'LayerFloorPlan': pya.LayerInfo(99, 0),
    'LayerPinRec' : pya.LayerInfo(69, 0),
    'LayerDevRec' : pya.LayerInfo(68, 0),
    'LayerFbrTgt' : pya.LayerInfo(81, 0),
    'LayerError' : pya.LayerInfo(999,0),
    'LayerLumerical' : pya.LayerInfo(733,0),
  },
  'EBeam': {
    'name' : 'EBeam',
    'library': 'EBeam',
    'LayerSi' : pya.LayerInfo(1, 0),
    'LayerText' : pya.LayerInfo(10, 0),
    'LayerSEM' : pya.LayerInfo(26, 0),
    'LayerSiP_6nm': pya.LayerInfo(31, 0),
    'LayerSiP_4nm': pya.LayerInfo(32, 0),
    'LayerSiP_2nm': pya.LayerInfo(33, 0),
    'LayerM1': pya.LayerInfo(11, 0),
    'LayerM2': pya.LayerInfo(12, 0),
    'LayerFloorPlan': pya.LayerInfo(99, 0),
    'LayerPinRec' : pya.LayerInfo(69, 0),
    'LayerDevRec' : pya.LayerInfo(68, 0),
    'LayerFbrTgt' : pya.LayerInfo(81, 0),
    'LayerError' : pya.LayerInfo(999,0),
    'LayerLumerical' : pya.LayerInfo(733,0),
  }
}
#Add alias for default
TECHNOLOGIES['default'] = TECHNOLOGIES['EBeam']
TECHNOLOGY = TECHNOLOGIES['default']

# Netlist extraction will merge straight+bend sections into waveguide (1), 
# or extract each bend, straight section, etc. (0)
#WAVEGUIDE_extract_simple = 1
SIMPLIFY_NETLIST_EXTRACTION = True

#Create GUI's
from .core import WaveguideGUI, MonteCarloGUI, CalibreGUI, Net
WG_GUI = WaveguideGUI()
MC_GUI = MonteCarloGUI()
DRC_GUI = CalibreGUI()
#Define global Net object that implements netlists and pin searching/connecting
NET = Net()

#Define enumeration for pins
from .utils import enum
PIN_TYPES = enum('I/O', 'OPTICAL', 'ELECTRICAL')

try:
  import numpy
except ImportError:
  MODULE_NUMPY = False
  
ACTIONS = []