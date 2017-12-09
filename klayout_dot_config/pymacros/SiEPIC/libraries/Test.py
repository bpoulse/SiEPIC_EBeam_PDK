import pya
from .. import _globals

class Photonic_Crystal(pya.PCellDeclarationHelper):
  def __init__(self):
    # Important: initialize the super class
    super(Photonic_Crystal, self).__init__()
    # declare the parameters
    self.param("type", self.TypeInt, "Type (Square = 0, Hexagonal = 1)", default = 0)
    self.param("lattice", self.TypeDouble, "Lattice (um)", default = 0.45)
    self.param("vsize", self.TypeInt, "Number Rows", default = 10)
    self.param("hsize", self.TypeInt, "Number Columns", default = 10)
    self.param("radius_b", self.TypeDouble, "Beginning Crystal Radius (um)", default = 0.15)
    self.param("radius_e", self.TypeDouble, "Ending Crystal Radius (um)", default = 0.16)
    self.param("n", self.TypeInt, "Number of Test Structures", default = 2)
    self.param("layer", self.TypeLayer, "Layer")
    
  def display_text_impl(self):
    return "Photonic_Crystal_Test_Structure"
        
  def produce_impl(self):
    from ..utils import arc
    from math import cos, pi, tan
    
    dbu = self.layout.dbu
    
    layer = self.layout.layer(self.layer)
    LayerExcludeN = self.layout.layer(_globals.TECHNOLOGY['LayerDRCexclude'])
    a = self.lattice/dbu
    a_r = pi*30/180
    v_s = self.vsize
    h_s = self.hsize
    r_b = self.radius_b/dbu
    r_e = self.radius_e/dbu
    n = self.n
    
    spacing = 3.0/dbu
    height = (a*(v_s-1) + 2*spacing) if self.type == 0 else (a*(v_s-1)*cos(a_r) + 2*spacing)
    width = (a*(h_s-1) + 2*spacing) if self.type == 0 else (a*(h_s-0.5) + 2*spacing)
    
    for m in range(0, n):
      origin = pya.Point(width*m, 0)
      r = r_b + m*(r_e-r_b)/n

      poly = pya.Polygon([pya.Point(0, 0),
                          pya.Point(0, height),
                          pya.Point(width, height),
                          pya.Point(width, 0)])

  
      if self.type == 0:
        drc_poly = pya.Polygon([pya.Point(-a/2,a/2),
                                pya.Point(a/2,a/2),
                                pya.Point(a/2,-a/2),
                                pya.Point(-a/2,-a/2)])
      else:
        drc_poly = pya.Polygon([pya.Point(a/2,round(a/2*tan(a_r),0)),
                                pya.Point(0,round(a/2/cos(a_r),0)),
                                pya.Point(-a/2,round(a/2*tan(a_r),0)),
                                pya.Point(-a/2,round(-a/2*tan(a_r),0)),
                                pya.Point(0,round(-a/2/cos(a_r),0)),
                                pya.Point(a/2,round(-a/2*tan(a_r),0))])
  
      # Create Photonic Crystal
      for i in range(0, v_s):
        for j in range(0, h_s):
          x = spacing + (j*a if self.type == 0 else (j*a + (0 if i%2 == 0 else a/2)))
          y = spacing + (i*a if self.type == 0 else i*a*cos(a_r))
          poly.insert_hole(pya.Polygon(arc(r, 0, 360)).transformed(pya.Trans(x, y)).get_points())
          self.cell.shapes(LayerExcludeN).insert(drc_poly.transformed(pya.Trans(origin.x + x, origin.y + y)))
  
      self.cell.shapes(layer).insert(poly.transformed(pya.Trans(origin.x, origin.y)))

class Test(pya.Library):
  def __init__(self):
    print("Initializing SiEPIC Test Structure Library.")

    self.description = ""
    
    import os
    self.layout().read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "SiEPIC-Test.gds"))
    [self.layout().rename_cell(i, self.layout().cell_name(i).replace('_', ' ')) for i in range(0, self.layout().cells())]
    
    self.layout().register_pcell("Photonic Crystal", Photonic_Crystal())
    
    self.register("SiEPIC Test Structure Library")