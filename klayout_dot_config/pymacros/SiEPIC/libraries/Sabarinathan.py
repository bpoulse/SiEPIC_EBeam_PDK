import pya
from .. import _globals

class PC_Hex_Ring_Resonator_Edge(pya.PCellDeclarationHelper):
  def __init__(self):
    # Important: initialize the super class
    super(PC_Hex_Ring_Resonator_Edge, self).__init__()
    # declare the parameters
    self.param("a", self.TypeDouble, "Lattice Size (um)", default = 0.45)
    self.param("r_h", self.TypeDouble, "Hole Radius (um)", default = 0.15)
    self.param("m", self.TypeDouble, "Edge Width (um)", default = 0.95*0.45)
    self.param("g", self.TypeDouble, "Coupler Gap (um)", default = 0.15)
    self.param("n", self.TypeDouble, "Number of basis cells from corner to corner (odd)", default = 37)
    self.param("c_w", self.TypeDouble, "Coupler width", default = 0.275)
    self.param("r_s", self.TypeDouble, "Radius of Center Support (um)", default = 2)
    self.param("e", self.TypeDouble, "Etch Distance (Added to Support, um)", default = 3)
    self.param("layerSi", self.TypeLayer, "Silicon Layer", default = _globals.TECHNOLOGY['LayerSi'])
    self.param("layerSiEtch", self.TypeLayer, "Silicon Etch Layer", default = _globals.TECHNOLOGY['LayerSiEtch2'])
    self.param("pinrec", self.TypeLayer, "PinRec Layer", default = _globals.TECHNOLOGY['LayerPinRec'])
    self.param("devrec", self.TypeLayer, "DevRec Layer", default = _globals.TECHNOLOGY['LayerDevRec'])

  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "PC_Hex_Ring_Resonator_Edge"
  
  def coerce_parameters_impl(self):
    pass

  def can_create_from_shape(self, layout, shape, layer):
    return False

  def produce_impl(self):
    from ..utils import arc, points_per_circle
    from math import pi, cos, sin, tan, log, sqrt, ceil
    # fetch the parameters
    dbu = self.layout.dbu
    ly = self.layout
    shapes = self.cell.shapes
    a = self.a/dbu
    r_h = self.r_h/dbu
    m = self.m/dbu
    g = self.g/dbu
    n = int(self.n)
    c_w = self.c_w/dbu
    r_s = self.r_s/dbu
    e = self.e/dbu
    LayerSiN = ly.layer(self.layerSi)
    LayerSiEtchN = ly.layer(self.layerSiEtch)
    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)
    LayerTextN = ly.layer(_globals.TECHNOLOGY['LayerText'])
    LayerExcludeN = ly.layer(_globals.TECHNOLOGY['LayerDRCexclude'])
    a_r = pi*30/180
    a_p = (n-1)*a/2+(m+r_h)/cos(a_r)

    # Create Photonic Crystal Ring Resonator
    poly = pya.Polygon([pya.Point(a_p*sin(a_r),a_p*cos(a_r)),
                        pya.Point(a_p,0),
                        pya.Point(a_p*sin(a_r),-a_p*cos(a_r)),
                        pya.Point(-a_p*sin(a_r),-a_p*cos(a_r)),
                        pya.Point(-a_p,0),
                        pya.Point(-a_p*sin(a_r),a_p*cos(a_r))])
                        
    mask_poly = pya.Polygon([pya.Point((a_p+g+c_w+2.0/dbu)*sin(a_r),(a_p+g+c_w+2.0/dbu)*cos(a_r)),
                    pya.Point((a_p+g+c_w+2.0/dbu),0),
                    pya.Point((a_p+g+c_w+2.0/dbu)*sin(a_r),-(a_p+g+c_w+2.0/dbu)*cos(a_r)),
                    pya.Point(-(a_p+g+c_w+2.0/dbu)*sin(a_r),-(a_p+g+c_w+2.0/dbu)*cos(a_r)),
                    pya.Point(-(a_p+g+c_w+2.0/dbu),0),
                    pya.Point(-(a_p+g+c_w+2.0/dbu)*sin(a_r),(a_p+g+c_w+2.0/dbu)*cos(a_r))])
                        
    drc_poly = pya.Polygon([pya.Point(a/2,round(a/2*tan(a_r),0)),
                        pya.Point(0,round(a/2/cos(a_r),0)),
                        pya.Point(-a/2,round(a/2*tan(a_r),0)),
                        pya.Point(-a/2,round(-a/2*tan(a_r),0)),
                        pya.Point(0,round(-a/2/cos(a_r),0)),
                        pya.Point(a/2,round(-a/2*tan(a_r),0))])

    # Create Photonic Crystal
    for i in range(0,ceil(n/2)):
      for j in range(0, n-i):
        x = -a*(n-1)/2 + j*a + i*a/2
        y = i*a*cos(a_r)
        if(sqrt(x*x+y*y)>(r_s+e)):
          if(i==0):
            hole = pya.Polygon(arc(r_h, 0, 360)).transformed(pya.Trans(x, 0)).get_points()
            poly.insert_hole(pya.Polygon(arc(r_h, 0, 360)).transformed(pya.Trans(x, 0)).get_points())
            shapes(LayerExcludeN).insert(drc_poly.transformed(pya.Trans(x, 0)))
          else:
            poly.insert_hole(pya.Polygon(arc(r_h, 0, 360)).transformed(pya.Trans(x, y)).get_points())
            poly.insert_hole(pya.Polygon(arc(r_h, 0, 360)).transformed(pya.Trans(x, -y)).get_points())
            shapes(LayerExcludeN).insert(drc_poly.transformed(pya.Trans(x, y)))
            shapes(LayerExcludeN).insert(drc_poly.transformed(pya.Trans(x, -y)))
            
    shapes(LayerSiN).insert(poly)
    shapes(ly.layer(pya.LayerInfo(50, 0))).insert(mask_poly)
    
    poly = pya.Polygon([pya.Point(a_p*sin(a_r),a_p*cos(a_r)+g),
                        pya.Point(a_p*sin(a_r)+10/dbu,a_p*cos(a_r)+g),
                        pya.Point(a_p*sin(a_r)+10/dbu,a_p*cos(a_r)+g+0.45/dbu),
                        pya.Point(a_p*sin(a_r),a_p*cos(a_r)+g+c_w),
                        pya.Point(-(a_p*sin(a_r)),a_p*cos(a_r)+g+c_w),
                        pya.Point(-(a_p*sin(a_r)+10/dbu),a_p*cos(a_r)+g+0.45/dbu),
                        pya.Point(-(a_p*sin(a_r)+10/dbu),a_p*cos(a_r)+g),
                        pya.Point(-(a_p*sin(a_r)),a_p*cos(a_r)+g)])
    
    shapes(LayerSiN).insert(poly)
    shapes(LayerSiN).insert(poly.transformed(pya.Trans(0, True, pya.Point(0,0))))
    
    poly = pya.Polygon([pya.Point(-(a_p*sin(a_r)+10.0/dbu),a_p*cos(a_r) + g + 3.0/dbu),
                        pya.Point(-(a_p*sin(a_r)+10.0/dbu),a_p*cos(a_r) + g - 2.0/dbu),
                        pya.Point(-(a_p*sin(a_r)+0.1/dbu),a_p*cos(a_r) + g -0.1/dbu),
                        pya.Point(-(a_p*sin(a_r)+0.1/dbu),a_p*cos(a_r) + g +c_w/2),
                        pya.Point(-(a_p*sin(a_r)+0.1/dbu),a_p*cos(a_r) + g + 3.0/dbu)])
    
    shapes(LayerSiEtchN).insert(poly)
    shapes(LayerSiEtchN).insert(poly.transformed(pya.Trans(0, True, pya.Point(0,0))))

    poly = pya.Polygon([pya.Point(a_p*sin(a_r)+0.1/dbu,a_p*cos(a_r) + g + 3.0/dbu),
                        pya.Point(a_p*sin(a_r)+0.1/dbu,a_p*cos(a_r) + g + c_w/2),
                        pya.Point(a_p*sin(a_r)+0.1/dbu,a_p*cos(a_r) + g - 0.1/dbu),
                        pya.Point(a_p*sin(a_r)+10.0/dbu,a_p*cos(a_r) + g - 2.0/dbu),
                        pya.Point(a_p*sin(a_r)+10.0/dbu,a_p*cos(a_r) + g + 3.0/dbu)])
    
    shapes(LayerSiEtchN).insert(poly)
    shapes(LayerSiEtchN).insert(poly.transformed(pya.Trans(0, True, pya.Point(0,0))))
    
    poly = pya.Polygon([pya.Point(a_p*sin(a_r)+10.0/dbu, a_p*cos(a_r) + g - 1.9/dbu),
                        pya.Point(a_p*sin(a_r)+10.0/dbu, -(a_p*cos(a_r) + g - 1.9/dbu)),
                        pya.Point(a_p-1.75/dbu, -(a_p*cos(a_r) + g - 0.5/dbu)),
                        pya.Point(a_p+2.0/dbu, 0),
                        pya.Point(a_p-1.75/dbu, a_p*cos(a_r) + g - 0.5/dbu)])
    
    shapes(LayerSiN).insert(poly)
    
    poly = pya.Box(a_p-0.5/dbu, -(a_p*cos(a_r) + g), a_p-2.25/dbu, -(a_p*cos(a_r) + g - 1.5/dbu))
    shapes(LayerExcludeN).insert(poly)
    shapes(LayerExcludeN).insert(poly.transformed(pya.Trans(0, True, pya.Point(0,0))))
    
    poly = pya.Box(-(a_p-0.5/dbu), -(a_p*cos(a_r) + g), -(a_p-2.25/dbu), -(a_p*cos(a_r) + g - 1.5/dbu))
    shapes(LayerExcludeN).insert(poly)
    shapes(LayerExcludeN).insert(poly.transformed(pya.Trans(0, True, pya.Point(0,0))))
    
    poly = pya.Polygon([pya.Point(-(a_p*sin(a_r)+10.0/dbu), a_p*cos(a_r) + g - 1.9/dbu),
                        pya.Point(-(a_p*sin(a_r)+10.0/dbu), -(a_p*cos(a_r) + g - 1.9/dbu)),
                        pya.Point(-(a_p-1.75/dbu), -(a_p*cos(a_r) + g - 0.5/dbu)),
                        pya.Point(-(a_p+2.0/dbu), 0),
                        pya.Point(-(a_p-1.75/dbu), a_p*cos(a_r) + g - 0.5/dbu)])
    
    shapes(LayerSiN).insert(poly)


    poly = pya.Polygon([pya.Point(a_p*sin(a_r)+10.0/dbu,a_p*cos(a_r) + g + 3.0/dbu),
                        pya.Point(-(a_p*sin(a_r)+10.0/dbu),a_p*cos(a_r) + g + 3.0/dbu),
                        pya.Point(-(a_p*sin(a_r)+10.0/dbu),-(a_p*cos(a_r) + g + 3.0/dbu)),
                        pya.Point(a_p*sin(a_r)+10.0/dbu,-(a_p*cos(a_r) + g + 3.0/dbu))])
    shapes(LayerDevRecN).insert(poly)
    
    if g < 0.2/dbu:
      poly = pya.Polygon([pya.Point(a_p*sin(a_r)+0.2/dbu,a_p*cos(a_r)-0.2/dbu),
                        pya.Point(a_p*sin(a_r)+0.2/dbu,a_p*cos(a_r)+g+0.2/dbu),
                        pya.Point(-(a_p*sin(a_r)+0.2/dbu),a_p*cos(a_r)+g+0.2/dbu),
                        pya.Point(-(a_p*sin(a_r)+0.2/dbu),a_p*cos(a_r)-0.2/dbu)])
      shapes(LayerExcludeN).insert(poly)
      shapes(LayerExcludeN).insert(poly.transformed(pya.Trans(0, True, 0, 0)))
    
    # Pins on the coupler:
    pin_length = 200

    t = pya.Trans(-(a_p*sin(a_r)+10.0/dbu),a_p*cos(a_r)+g+0.45/dbu/2)
    shapes(LayerPinRecN).insert(pya.Path([pya.Point(-pin_length/2, 0), pya.Point(pin_length/2, 0)], 4.45/dbu).transformed(t))
    shapes(LayerPinRecN).insert(pya.Text("pin1", t)).text_size = 0.4/dbu

    t = pya.Trans(a_p*sin(a_r)+10.0/dbu,a_p*cos(a_r)+g+0.45/dbu/2)
    shapes(LayerPinRecN).insert(pya.Path([pya.Point(-pin_length/2, 0), pya.Point(pin_length/2, 0)], 4.45/dbu).transformed(t))
    shapes(LayerPinRecN).insert(pya.Text("pin2", t)).text_size = 0.4/dbu
    
    t = pya.Trans(-(a_p*sin(a_r)+10.0/dbu),-(a_p*cos(a_r)+g+0.45/dbu/2))
    shapes(LayerPinRecN).insert(pya.Path([pya.Point(-pin_length/2, 0), pya.Point(pin_length/2, 0)], 4.45/dbu).transformed(t))
    shapes(LayerPinRecN).insert(pya.Text("pin3", t)).text_size = 0.4/dbu

    t = pya.Trans(a_p*sin(a_r)+10.0/dbu,-(a_p*cos(a_r)+g+0.45/dbu/2))
    shapes(LayerPinRecN).insert(pya.Path([pya.Point(-pin_length/2, 0), pya.Point(pin_length/2, 0)], 4.45/dbu).transformed(t))
    shapes(LayerPinRecN).insert(pya.Text("pin4", t)).text_size = 0.4/dbu

class Ridge_Strip(pya.PCellDeclarationHelper):
  def __init__(self):
    # Important: initialize the super class
    super(Ridge_Strip, self).__init__()
    # declare the parameters
    self.param("rw1", self.TypeDouble, "Ridge Outer Width", default = 4.45)
    self.param("rw2", self.TypeDouble, "Ridge Inner Width", default = 0.45)
    self.param("sw", self.TypeDouble, "Slab Width", default = 0.5)
    self.param("l", self.TypeDouble, "Length", default = 20.0)
    self.param("layerSi", self.TypeLayer, "Silicon Layer", default = _globals.TECHNOLOGY['LayerSi'])
    self.param("layerSiEtch", self.TypeLayer, "Ridge Layer", default = _globals.TECHNOLOGY['LayerSiEtch2'])

  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "Ridge_Strip"
  
  def coerce_parameters_impl(self):
    pass

  def can_create_from_shape(self, layout, shape, layer):
    return False

  def produce_impl(self):
    # fetch the parameters
    dbu = self.layout.dbu
    ly = self.layout
    shapes = self.cell.shapes
    w1 = self.rw1/dbu
    w2 = self.rw2/dbu
    w3 = self.sw/dbu
    l = self.l/dbu
    LayerSiN = ly.layer(self.layerSi)
    LayerSiEtchN = ly.layer(self.layerSiEtch)
    LayerPinRecN = ly.layer(_globals.TECHNOLOGY['LayerPinRec'])
    LayerDevRecN = ly.layer(_globals.TECHNOLOGY['LayerDevRec'])
    LayerTextN = ly.layer(_globals.TECHNOLOGY['LayerText'])

    shapes(LayerSiEtchN).insert(pya.Polygon([pya.Point(-l, w1/2), pya.Point(-l, -w1/2), pya.Point(0, -w3/2 - 0.1/dbu), pya.Point(0, w3/2 + 0.1/dbu)]))
    shapes(LayerSiN).insert(pya.Polygon([pya.Point(-l, w2/2), pya.Point(-l, -w2/2), pya.Point(0, -w3/2), pya.Point(0, w3/2)]))
    shapes(LayerDevRecN).insert(pya.Polygon([pya.Point(-l, w1/2), pya.Point(-l, -w1/2), pya.Point(0, -w1/2), pya.Point(0, w1/2)]))

    # Pins on the coupler:
    pin_length = 200

    t = pya.Trans(-l, 0)
    shapes(LayerPinRecN).insert(pya.Path([pya.Point(-pin_length/2, 0), pya.Point(pin_length/2, 0)], w1).transformed(t))
    shapes(LayerPinRecN).insert(pya.Text("pin1", t)).text_size = 0.4/dbu

    t = pya.Trans(0, 0)
    shapes(LayerPinRecN).insert(pya.Path([pya.Point(-pin_length/2, 0), pya.Point(pin_length/2, 0)], w3).transformed(t))
    shapes(LayerPinRecN).insert(pya.Text("pin2", t)).text_size = 0.4/dbu
    
class Sabarinathan(pya.Library):
  def __init__(self):
    print("Initializing Sabarinathan Lab Library.")

    self.description = ""

    import os
    self.layout().read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "Sabarinathan-GSiP.gds"))
    [self.layout().rename_cell(i, self.layout().cell_name(i).replace('_', ' ')) for i in range(0, self.layout().cells())]
    
    self.layout().register_pcell("Photonic Crystal Hexagonal Ring Resonator", PC_Hex_Ring_Resonator_Edge())
    self.layout().register_pcell("Ridge to Strip Coupler", Ridge_Strip())
    
    self.register("Sabarinathan Lab Library")