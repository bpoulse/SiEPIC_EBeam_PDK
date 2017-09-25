import pya
from .. import _globals

class EBeam(pya.Library):
  def __init__(self):
    print("Initializing SiEPIC EBeam library.")

    self.description = ""
    
    import os
    self.layout().read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "SiEPIC-EBeam.gds"))
    [self.layout().rename_cell(i, self.layout().cell_name(i).replace('_', ' ')) for i in range(0, self.layout().cells())]
    
    self.register("SiEPIC EBeam Library")