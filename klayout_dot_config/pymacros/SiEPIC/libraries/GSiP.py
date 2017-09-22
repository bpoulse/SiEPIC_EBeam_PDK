import pya
from .. import _globals

class Ring_Modulator_DB(pya.PCellDeclarationHelper):
  """
  The PCell declaration for ring modulator.
  Consists of a ring with 2 straight waveguides
  With pn junction and heater
  Written by Anthony Park and Wei Shi, 2017
  """
  def __init__(self):
    super(Ring_Modulator_DB, self).__init__()
    # declare the parameters
    self.param("silayer", self.TypeLayer, "Si Layer", default = _globals.TECHNOLOGY['LayerSi'])
    self.param("s", self.TypeShape, "", default = pya.DPoint(0, 0))
    self.param("r", self.TypeDouble, "Radius", default = 10)
    self.param("w", self.TypeDouble, "Waveguide Width", default = 0.5)
    self.param("g", self.TypeDouble, "Gap", default = 0.2)
    self.param("gmon", self.TypeDouble, "Gap Monitor", default = 0.5)
    self.param("si3layer", self.TypeLayer, "SiEtch2(Rib) Layer", default = _globals.TECHNOLOGY['LayerSiEtch2'])
    self.param("nlayer", self.TypeLayer, "N Layer", default = _globals.TECHNOLOGY['LayerSiN'])
    self.param("player", self.TypeLayer, "P Layer", default = _globals.TECHNOLOGY['LayerSiP'])
    self.param("nplayer", self.TypeLayer, "N+ Layer", default = _globals.TECHNOLOGY['LayerSiN+'])
    self.param("pplayer", self.TypeLayer, "P+ Layer", default = _globals.TECHNOLOGY['LayerSiP+'])
    self.param("npplayer", self.TypeLayer, "N++ Layer", default = _globals.TECHNOLOGY['LayerSiN++'])
    self.param("ppplayer", self.TypeLayer, "P++ Layer", default = _globals.TECHNOLOGY['LayerSiP++'])
    self.param("vclayer", self.TypeLayer, "VC Layer", default = _globals.TECHNOLOGY['LayerVC'])
    self.param("m1layer", self.TypeLayer, "M1 Layer", default = _globals.TECHNOLOGY['LayerM1'])
    self.param("vllayer", self.TypeLayer, "VL Layer", default = _globals.TECHNOLOGY['LayerVL'])
    self.param("mllayer", self.TypeLayer, "ML Layer", default = _globals.TECHNOLOGY['LayerSi'])
    self.param("mhlayer", self.TypeLayer, "MH Layer", default = _globals.TECHNOLOGY['LayerMHeater'])
    self.param("textpolygon", self.TypeInt, "Draw text polygon label? 0/1", default = 1)
    self.param("textl", self.TypeLayer, "Text Layer", default = _globals.TECHNOLOGY['LayerText'])
    self.param("pinrec", self.TypeLayer, "PinRec Layer", default = _globals.TECHNOLOGY['LayerPinRec'])
    self.param("devrec", self.TypeLayer, "DevRec Layer", default = _globals.TECHNOLOGY['LayerDevRec'])

  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "Ring_Modulator_DB(R=" + ('%.3f' % self.r) + ",g=" + ('%g' % (1000*self.g)) + ")"

  def can_create_from_shape_impl(self):
    return False
    
  def produce_impl(self):
    # This is the main part of the implementation: create the layout
    from math import pi, cos, sin
    
    # fetch the parameters
    dbu = self.layout.dbu
    ly = self.layout
    shapes = self.cell.shapes
    
    LayerSi = self.silayer
    LayerSi3 = ly.layer(self.si3layer)
    LayerSiN = ly.layer(LayerSi)
    LayernN = ly.layer(self.nlayer)
    LayerpN = ly.layer(self.player)
    LayernpN = ly.layer(self.nplayer)
    LayerppN = ly.layer(self.pplayer)
    LayernppN = ly.layer(self.npplayer)
    LayerpppN = ly.layer(self.ppplayer)
    LayervcN = ly.layer(self.vclayer)
    Layerm1N = ly.layer(self.m1layer)
    LayervlN = ly.layer(self.vllayer)
    LayermlN = ly.layer(self.mllayer)
    LayermhN = ly.layer(self.mhlayer)
    TextLayerN = ly.layer(self.textl)
    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)
    
    # Define variables for the Modulator
    # Variables for the Si waveguide
    w = self.w/dbu
    r = self.r/dbu
    g = self.g/dbu
    gmon = self.gmon/dbu
    
    #Variables for the N layer
    w_1 = 2.0/dbu  #same for N, P, N+, P+ layer
    r_n = (self.r - 1.0)/dbu
    
    #Variables for the P layer
    r_p = (self.r + 1.0)/dbu
     
    #Variables for the N+layer
    r_np = (self.r - 1.5)/dbu
    
    #Variables for the P+layer
    r_pp = (self.r + 1.5)/dbu

    #Variables for the N++ layer
    w_2 = 5.5/dbu  #same for N++, P++ layer
    r_npp = (self.r - 3.75)/dbu

    #Variables for the P+layer
    r_ppp = (self.r + 3.75)/dbu

    #Variables for the VC layer
    w_vc = 4.0/dbu
    r_vc1 = (self.r - 3.75)/dbu
    r_vc2 = (self.r + 3.75)/dbu
   
    #Variables for the M1 layer
    w_m1_in = (r_vc1 + w_vc/2.0 + 0.5/dbu)
    r_m1_in = (r_vc1 + w_vc/2.0 + 0.5/dbu) /2.0
    w_m1_out = 6.0/dbu
    r_m1_out = (self.r + 4.25)/dbu
    
    #Variables for the VL layer
    #r_vl =  w_m1_in/2.0 -  2.1/dbu
    r_vl =  r_vc1 - w_vc/2.0 - 2.01/dbu
    if r_vl < 1.42/dbu:
      r_vl = 1.42/dbu
      w_vc = (self.r-1.75)/dbu - (r_vl + 2.01)
      r_vc1 = (self.r-1.75)/dbu - w_vc/2.0
      r_vc2 = (self.r+1.75)/dbu + w_vc/2.0
      w_2 = (r-w/2.0 - 0.75/dbu) - (r_vc1 - w_vc/2.0 - 0.75) # same for N++, P++ layer
      r_npp = ((r-w/2.0 - 0.75/dbu) + (r_vc1 - w_vc/2.0 - 0.75))/2.0
      r_ppp = 2*(self.r)/dbu - r_npp
    w_via = 5.0/dbu
    h_via = 5.0/dbu

    # Variables for the SiEtch2 layer  (Slab)
    w_Si3 = w_m1_out + 2*(r_m1_out)+ 0/dbu
    h_Si3 = w_Si3
    taper_bigend =  2/dbu
    taper_smallend =  0.3/dbu
    taper_length =  5/dbu

    #Variables for the MH layer
    w_mh = 2.0/dbu
    r_mh = self.r/dbu
    r_mh_in = r_mh - w_mh/2.0
    
    #Define Ring centre   
    x0 = r + w/2
    y0 = r + g + w 

    ######################
    # Generate the layout:
   
    # Create the ring resonator
    t = pya.Trans(x0, y0)
    pcell = ly.create_cell("Ring", "SiEPIC Common Library", { "layer": _globals.TECHNOLOGY['LayerSi'], "radius": self.r, "width": self.w } )
    self.cell.insert(pya.CellInstArray(pcell.cell_index(), t))
    
    # Create the two waveguides
    wg1 = pya.Box(x0 - (w_Si3 / 2 + taper_length), -w/2, x0 + (w_Si3 / 2 + taper_length), w/2)
    shapes(LayerSiN).insert(wg1)
    y_offset = 2*r + g + gmon + 2*w
    wg2 = pya.Box(x0 - (w_Si3 / 2 + taper_length), y_offset-w/2, x0 + (w_Si3 / 2 + taper_length), y_offset+w/2)
    shapes(LayerSiN).insert(wg2)

    
    #Create the SiEtch2 (Slab) layer
    boxSi3 = pya.Box(x0-w_Si3/2.0, y0 - h_Si3/2.0, x0+w_Si3/2.0, y0 + h_Si3/2.0)
    shapes(LayerSi3).insert(boxSi3)
    pin1pts = [pya.Point(x0-w_Si3/2.0, -taper_bigend/2.0),
               pya.Point(x0-w_Si3/2.0-taper_length,-taper_smallend/2.0),
               pya.Point(x0-w_Si3/2.0-taper_length,taper_smallend/2.0),
               pya.Point(x0-w_Si3/2.0, taper_bigend/2.0)]
    pin2pts = [pya.Point(x0+w_Si3/2.0,-taper_bigend/2.0),
               pya.Point(x0+w_Si3/2.0+taper_length,-taper_smallend/2.0),
               pya.Point(x0+w_Si3/2.0+taper_length,taper_smallend/2.0),
               pya.Point(x0+w_Si3/2.0,+taper_bigend/2.0)]
    pin3pts = [pya.Point(x0-w_Si3/2.0,y_offset-taper_bigend/2.0),
               pya.Point(x0-w_Si3/2.0-taper_length,y_offset-taper_smallend/2.0),
               pya.Point(x0-w_Si3/2.0-taper_length,y_offset+taper_smallend/2.0),
               pya.Point(x0-w_Si3/2.0,y_offset+ taper_bigend/2.0)]
    pin4pts = [pya.Point(x0+w_Si3/2.0,y_offset-taper_bigend/2.0),
               pya.Point(x0+w_Si3/2.0+taper_length,y_offset-taper_smallend/2.0),
               pya.Point(x0+w_Si3/2.0+taper_length,y_offset+taper_smallend/2.0),
               pya.Point(x0+w_Si3/2.0,y_offset+taper_bigend/2.0)]
    shapes(LayerSi3).insert(pya.Polygon(pin1pts))
    shapes(LayerSi3).insert(pya.Polygon(pin2pts))
    shapes(LayerSi3).insert(pya.Polygon(pin3pts))
    shapes(LayerSi3).insert(pya.Polygon(pin4pts))
    
    # arc angles
    # doping:
    angle_min_doping = -35
    angle_max_doping = 215
    # VC contact:
    angle_min_VC = angle_min_doping + 8
    angle_max_VC = angle_max_doping - 8
    # M1:
    angle_min_M1 = angle_min_VC - 4
    angle_max_M1 = angle_max_VC + 4
    # MH:
    angle_min_MH = -75.0
    angle_max_MH = 255

    from ..utils import arc

    #Create the N Layer
    self.cell.shapes(LayernN).insert(pya.Path(arc(r_n, angle_min_doping, angle_max_doping), w_1).transformed(t).simple_polygon())

    #Create the P Layer
    self.cell.shapes(LayerpN).insert(pya.Path(arc(r_p, angle_min_doping, angle_max_doping), w_1).transformed(t).simple_polygon())
    
    #Create the N+ Layer
    self.cell.shapes(LayernpN).insert(pya.Path(arc(r_np, angle_min_doping, angle_max_doping), w_1).transformed(t).simple_polygon())

    #Create the P+ Layer
    self.cell.shapes(LayerppN).insert(pya.Path(arc(r_pp, angle_min_doping, angle_max_doping), w_1).transformed(t).simple_polygon())
    
    #Create the N++ Layer
    self.cell.shapes(LayernppN).insert(pya.Path(arc(r_npp, angle_min_doping, angle_max_doping), w_1).transformed(t).simple_polygon())

    #Create the P+ +Layer
    poly = pya.Path(arc(r_ppp, angle_min_doping, angle_max_doping), w_2).transformed(t).simple_polygon()
    self.cell.shapes(LayerpppN).insert(pya.Region(poly) - pya.Region(pya.Box(x0-r_ppp-w_2/2, y_offset-w/2 - 0.75/dbu, x0+r_ppp+w/2, y_offset+w/2 + 0.75/dbu)))
    
    #Create the VC Layer
    self.cell.shapes(LayervcN).insert(pya.Path(arc(r_vc1, angle_min_VC, angle_max_VC), w_vc).transformed(t).simple_polygon())

    poly = pya.Path(arc(r_vc2, angle_min_VC, angle_max_VC), w_vc).transformed(t).simple_polygon()
    self.cell.shapes(LayervcN).insert(pya.Region(poly) - pya.Region(pya.Box(x0-r_vc2-w_vc/2, y_offset-w/2 - 1.5/dbu, x0+r_vc2+w_vc/2, y_offset+w/2 + 1.5/dbu)))
    
    #Create the M1 Layer
    self.cell.shapes(Layerm1N).insert(pya.Polygon(arc(w_m1_in, angle_min_doping, angle_max_doping) + [pya.Point(-w_m1_in, w_m1_in)]).transformed(t))
    self.cell.shapes(Layerm1N).insert(pya.Polygon(arc(w_m1_in/2.0, 0, 360)).transformed(t))
    self.cell.shapes(Layerm1N).insert(pya.Path(arc(r_m1_out, angle_min_M1, angle_max_M1), w_m1_out).transformed(t).simple_polygon())

    boxM11 = pya.Box(x0-w_via, y0 + r_m1_out + w_m1_out-h_via, x0+w_via, y0 + r_m1_out + w_m1_out+h_via)
    shapes(Layerm1N).insert(boxM11)
    
    #Create the ML Layer
    self.cell.shapes(LayermlN).insert(pya.Polygon(arc(w_m1_in/2.0, 0, 360)).transformed(t))
    
    #Create the VL Layer, as well as the electrical PinRec geometries
    # centre contact (P, anode):
    self.cell.shapes(LayervlN).insert(pya.Polygon(arc(r_vl, 0, 360)).transformed(t))
    self.cell.shapes(LayerPinRecN).insert(pya.Polygon(arc(r_vl, 0, 360)).transformed(t))
    shapes(LayerPinRecN).insert(pya.Text ("elec1a", pya.Trans(x0,y0))).text_size = 0.5/dbu
    shapes(LayerPinRecN).insert(pya.Box(x0-w_via/2, y0-w_via/2, x0+w_via/2, y0+w_via/2))
    
    # top contact (N, cathode):
    boxVL1 = pya.Box(x0-w_via/2, y0 +  r_vc2 +  w_vc/2 + 2.0/dbu, x0+w_via/2, y0 + r_vc2 +  w_vc/2 + 2.0/dbu+ h_via)
    shapes(LayervlN).insert(boxVL1)
    shapes(LayerPinRecN).insert(boxVL1)
    shapes(LayerPinRecN).insert(pya.Text ("elec1c", pya.Trans(x0,y0 + r_vc2 +  w_vc/2 + 2.0/dbu+ h_via/2))).text_size = 0.5/dbu
    # heater contacts
    boxVL3 = pya.Box(x0+(r_mh_in)*cos(angle_min_MH/180*pi) + 2.5/dbu, -w/2.0 -  10/dbu, x0 + (r_mh_in)*cos(angle_min_MH/180*pi) + 7.5/dbu, -w/2.0 -  5/dbu)
    shapes(LayervlN).insert(boxVL3)
    shapes(LayerPinRecN).insert(boxVL3)
    shapes(LayerPinRecN).insert(pya.Text ("elec2h2", pya.Trans(x0+(r_mh_in)*cos(angle_min_MH/180*pi) + 5.0/dbu,-w/2.0 -  7.5/dbu))).text_size = 0.5/dbu
    boxVL4 = pya.Box(x0-(r_mh_in)*cos(angle_min_MH/180*pi)- 7.5/dbu, -w/2.0 -  10/dbu, x0 - (r_mh_in)*cos(angle_min_MH/180*pi) - 2.5/dbu, -w/2.0 -  5/dbu)
    shapes(LayervlN).insert(boxVL4)
    shapes(LayerPinRecN).insert(boxVL4)
    shapes(LayerPinRecN).insert(pya.Text ("elec2h1", pya.Trans(x0-(r_mh_in)*cos(angle_min_MH/180*pi) - 5.0/dbu,-w/2.0 -  7.5/dbu))).text_size = 0.5/dbu

    #Create the MH Layer
    self.cell.shapes(LayermhN).insert(pya.Path(arc(r_mh, angle_min_MH, angle_max_MH), w_mh).transformed(t).simple_polygon())
    boxMH1 = pya.Box(x0+(r_mh_in)*cos(angle_min_MH/180*pi), -w/2.0 -  2.5/dbu, x0 + (r_mh_in)*cos(angle_min_MH/180*pi) + w_mh, y0 +(r_mh_in)*sin(angle_min_MH/180*pi))
    shapes(LayermhN).insert(boxMH1)
    boxMH2 = pya.Box(x0-(r_mh_in)*cos(angle_min_MH/180*pi)  - w_mh, -w/2.0 -  2.5/dbu, x0 - (r_mh_in)*cos(angle_min_MH/180*pi), y0 +(r_mh_in)*sin(angle_min_MH/180*pi))
    shapes(LayermhN).insert(boxMH2)
    boxMH3 = pya.Box(x0+(r_mh_in)*cos(angle_min_MH/180*pi), -w/2.0 -  12.5/dbu, x0 + (r_mh_in)*cos(angle_min_MH/180*pi) + 10/dbu, -w/2.0 -  2.5/dbu)
    shapes(LayermhN).insert(boxMH3)
    boxMH4 = pya.Box(x0-(r_mh_in)*cos(angle_min_MH/180*pi)- 10/dbu, -w/2.0 -  12.5/dbu, x0 - (r_mh_in)*cos(angle_min_MH/180*pi), -w/2.0 -  2.5/dbu)
    shapes(LayermhN).insert(boxMH4)
    
    # Create the pins, as short paths:
    pin_length = 200 # database units, = 0.2 microns
    
    shapes(LayerPinRecN).insert(pya.Path([pya.Point(x0 - (w_Si3 / 2 + taper_length)- pin_length/2, 0),
                                          pya.Point(x0 - (w_Si3 / 2 + taper_length) + pin_length/2, 0)], w))
    shapes(LayerPinRecN).insert(pya.Text("opt1", pya.Trans(x0 - (w_Si3 / 2 + taper_length), 0))).text_size = 0.5/dbu

    shapes(LayerPinRecN).insert(pya.Path([pya.Point(x0 + (w_Si3 / 2 + taper_length)-pin_length/2, 0),
                                pya.Point(x0 + (w_Si3 / 2 + taper_length) + pin_length/2, 0)], w))
    shapes(LayerPinRecN).insert(pya.Text("opt2", pya.Trans(x0 + (w_Si3 / 2 + taper_length), 0))).text_size = 0.5/dbu

    shapes(LayerPinRecN).insert(pya.Path([pya.Point(x0 - (w_Si3 / 2 + taper_length)- pin_length/2, y_offset),
                                          pya.Point(x0 - (w_Si3 / 2 + taper_length)+ pin_length/2, y_offset)], w))
    shapes(LayerPinRecN).insert(pya.Text("opt3", pya.Trans(x0 - (w_Si3 / 2 + taper_length), y_offset))).text_size = 0.5/dbu

    shapes(LayerPinRecN).insert(pya.Path([pya.Point(x0 + (w_Si3 / 2 + taper_length)-pin_length/2, y_offset),
                                          pya.Point(x0 + (w_Si3 / 2 + taper_length)+ pin_length/2, y_offset)], w))
    shapes(LayerPinRecN).insert(pya.Text("opt4", pya.Trans(x0 + (w_Si3 / 2 + taper_length), y_offset))).text_size = 0.5/dbu

    # Create the device recognition layer
    shapes(LayerDevRecN).insert(pya.Box(x0 - (w_Si3 / 2 + taper_length), -w/2.0 -  12.5/dbu, x0 + (w_Si3 / 2 + taper_length), y0 + r_m1_out + w_m1_out+h_via ))

    # Compact model information
    shape = shapes(LayerDevRecN).insert(pya.Text('Lumerical_INTERCONNECT_library=Design kits/GSiP', \
      pya.Trans(0, 0))).text_size = 0.3/dbu
    shapes(LayerDevRecN).insert(pya.Text('Lumerical_INTERCONNECT_component=Ring_Modulator_DB', \
      pya.Trans(0, w*2))).text_size = 0.3/dbu
    shapes(LayerDevRecN).insert(pya.Text \
      ('Spice_param:radius=%.3fu wg_width=%.3fu gap=%.3fu gap_monitor=%.3fu' %\
      (self.r, self.w, self.g, self.gmon), \
      pya.Trans(0, -w*2) ) ).text_size = 0.3/dbu
    
    # Add a polygon text description
    from ..utils import layout_pgtext
    if self.textpolygon : layout_pgtext(self.cell, self.textl, self.w, self.r+self.w, "%.3f-%g" % ( self.r, self.g), 1)

    # Reference publication:
    shapes(TextLayerN).insert(pya.Text ("Ref: Raphael Dube-Demers, JLT, 2015", pya.Trans(x0 - (w_Si3 / 2 + taper_length), -w/2.0 -  12.5/dbu+4.0/dbu))).text_size = 0.7/dbu
    shapes(TextLayerN).insert(pya.Text ("http://dx.doi.org/10.1109/JLT.2015.2462804", pya.Trans(x0 - (w_Si3 / 2 + taper_length), -w/2.0 -  12.5/dbu+1.0/dbu))).text_size = 0.7/dbu

class Ring_Filter_DB(pya.PCellDeclarationHelper):
  """
  The PCell declaration for thermally tunable ring filter.
  """
  def __init__(self):
    super(Ring_Filter_DB, self).__init__()
    # declare the parameters
    self.param("silayer", self.TypeLayer, "Si Layer", default = _globals.TECHNOLOGY['LayerSi'])
    self.param("s", self.TypeShape, "", default = pya.DPoint(0, 0))
    self.param("r", self.TypeDouble, "Radius", default = 10)
    self.param("w", self.TypeDouble, "Waveguide Width", default = 0.5)
    self.param("g", self.TypeDouble, "Gap", default = 0.2)
    self.param("gmon", self.TypeDouble, "Gap Monitor", default = 0.5)
    self.param("si3layer", self.TypeLayer, "SiEtch2(Rib) Layer", default = _globals.TECHNOLOGY['LayerSiEtch2'])
    self.param("vllayer", self.TypeLayer, "VL Layer", default = _globals.TECHNOLOGY['LayerVL'])
    self.param("mllayer", self.TypeLayer, "ML Layer", default = _globals.TECHNOLOGY['LayerML'])
    self.param("mhlayer", self.TypeLayer, "MH Layer", default = _globals.TECHNOLOGY['LayerMHeater'])
    self.param("textpolygon", self.TypeInt, "Draw text polygon label? 0/1", default = 1)
    self.param("textl", self.TypeLayer, "Text Layer", default = _globals.TECHNOLOGY['LayerText'])
    self.param("pinrec", self.TypeLayer, "PinRec Layer", default = _globals.TECHNOLOGY['LayerPinRec'])
    self.param("devrec", self.TypeLayer, "DevRec Layer", default = _globals.TECHNOLOGY['LayerDevRec'])

  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "Ring_Filter_DB(R=" + ('%.3f' % self.r) + ",g=" + ('%g' % (1000*self.g)) + ")"

  def can_create_from_shape_impl(self):
    return False
    
  def produce_impl(self):
    # This is the main part of the implementation: create the layout
    from math import pi, cos, sin
    
    # fetch the parameters
    dbu = self.layout.dbu
    ly = self.layout
    shapes = self.cell.shapes
    
    LayerSi = self.silayer
    LayerSi3 = ly.layer(self.si3layer)
    LayerSiN = ly.layer(LayerSi)
    LayervlN = ly.layer(self.vllayer)
    LayermlN = ly.layer(self.mllayer)
    LayermhN = ly.layer(self.mhlayer)
    TextLayerN = ly.layer(self.textl)
    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)

    
    # Define variables for the Modulator
    # Variables for the Si waveguide
    w = self.w/dbu
    r = self.r/dbu
    g = self.g/dbu
    gmon = self.gmon/dbu
    
    #Variables for the N layer
    w_1 = 2.0/dbu  #same for N, P, N+, P+ layer
    r_n = (self.r - 1.0)/dbu

    #Variables for the VC layer
    w_vc = 4.0/dbu
    r_vc1 = (self.r - 3.75)/dbu
    r_vc2 = (self.r + 3.75)/dbu
   
    #Variables for the M1 layer
    w_m1_in = (r_vc1 + w_vc/2.0 + 0.5/dbu)
    r_m1_in = (r_vc1 + w_vc/2.0 + 0.5/dbu) /2.0
    w_m1_out = 6.0/dbu
    r_m1_out = (self.r + 4.25)/dbu
    
    #Variables for the VL layer
    r_vl =  w_m1_in/2.0 -  2.1/dbu
    w_via = 5.0/dbu
    h_via = 5.0/dbu

    # Variables for the SiEtch2 layer  (Slab)
    w_Si3 = w_m1_out + 2*(r_m1_out)+ 0/dbu
    h_Si3 = w_Si3
    taper_bigend =  2/dbu
    taper_smallend =  0.3/dbu
    taper_length =  5/dbu

    #Variables for the MH layer
    w_mh = 2.0/dbu
    r_mh = self.r/dbu
    r_mh_in = r_mh - w_mh/2.0
    
    #Define Ring centre   
    x0 = r + w/2
    y0 = r + g + w 

    ######################
    # Generate the layout:
   
    # Create the ring resonator
    t = pya.Trans((self.r+self.w/2)/dbu, (self.r+self.g+self.w)/dbu)
    pcell = ly.create_cell("Ring", "SiEPIC Common Library", { "layer": _globals.TECHNOLOGY['LayerSi'], "radius": self.r, "width": self.w } )
    self.cell.insert(pya.CellInstArray(pcell.cell_index(), t))
    
    # Create the two waveguides
    wg1 = pya.Box(x0 - (w_Si3 / 2 + taper_length), -w/2, x0 + (w_Si3 / 2 + taper_length), w/2)
    shapes(LayerSiN).insert(wg1)
    y_offset = 2*r + g + gmon + 2*w
    wg2 = pya.Box(x0 - (w_Si3 / 2 + taper_length), y_offset-w/2, x0 + (w_Si3 / 2 + taper_length), y_offset+w/2)
    shapes(LayerSiN).insert(wg2)
    
    #Create the SiEtch2 (Slab) layer
    boxSi3 = pya.Box(x0-w_Si3/2.0, y0 - h_Si3/2.0, x0+w_Si3/2.0, y0 + h_Si3/2.0)
    shapes(LayerSi3).insert(boxSi3)
    pin1pts = [pya.Point(x0-w_Si3/2.0,-taper_bigend/2.0), pya.Point(x0-w_Si3/2.0-taper_length,-taper_smallend/2.0), pya.Point(x0-w_Si3/2.0-taper_length,taper_smallend/2.0), pya.Point(x0-w_Si3/2.0, taper_bigend/2.0)]
    pin2pts = [pya.Point(x0+w_Si3/2.0,-taper_bigend/2.0), pya.Point(x0+w_Si3/2.0+taper_length,-taper_smallend/2.0), pya.Point(x0+w_Si3/2.0+taper_length,taper_smallend/2.0), pya.Point(x0+w_Si3/2.0,+taper_bigend/2.0)]
    pin3pts = [pya.Point(x0-w_Si3/2.0,y_offset-taper_bigend/2.0), pya.Point(x0-w_Si3/2.0-taper_length,y_offset-taper_smallend/2.0), pya.Point(x0-w_Si3/2.0-taper_length,y_offset+taper_smallend/2.0),pya. Point(x0-w_Si3/2.0,y_offset+ taper_bigend/2.0)]
    pin4pts = [pya.Point(x0+w_Si3/2.0,y_offset-taper_bigend/2.0), pya.Point(x0+w_Si3/2.0+taper_length,y_offset-taper_smallend/2.0), pya.Point(x0+w_Si3/2.0+taper_length,y_offset+taper_smallend/2.0), pya.Point(x0+w_Si3/2.0,y_offset+taper_bigend/2.0)]
    shapes(LayerSi3).insert(pya.Polygon(pin1pts))
    shapes(LayerSi3).insert(pya.Polygon(pin2pts))
    shapes(LayerSi3).insert(pya.Polygon(pin3pts))
    shapes(LayerSi3).insert(pya.Polygon(pin4pts))
    
    from ..utils import arc
    
    # arc angles
    # doping:
    angle_min_doping = -35
    angle_max_doping = 215
    # VC contact:
    angle_min_VC = angle_min_doping + 8
    angle_max_VC = angle_max_doping - 8
    # M1:
    angle_min_M1 = angle_min_VC - 4
    angle_max_M1 = angle_max_VC + 4
    # MH:
    angle_min_MH = -75.0
    angle_max_MH = 255
    
    #Create the VL Layer, as well as the electrical PinRec geometries
    # heater contacts
    boxVL3 = pya.Box(x0+(r_mh_in)*cos(angle_min_MH/180*pi) + 2.5/dbu, -w/2.0 -  10/dbu, x0 + (r_mh_in)*cos(angle_min_MH/180*pi) + 7.5/dbu, -w/2.0 -  5/dbu)
    shapes(LayervlN).insert(boxVL3)
    shapes(LayerPinRecN).insert(boxVL3)
    shapes(LayerPinRecN).insert(pya.Text ("elec2h2", pya.Trans(x0+(r_mh_in)*cos(angle_min_MH/180*pi) + 5.0/dbu,-w/2.0 -  7.5/dbu))).text_size = 0.5/dbu
    boxVL4 = pya.Box(x0-(r_mh_in)*cos(angle_min_MH/180*pi)- 7.5/dbu, -w/2.0 -  10/dbu, x0 - (r_mh_in)*cos(angle_min_MH/180*pi) - 2.5/dbu, -w/2.0 -  5/dbu)
    shapes(LayervlN).insert(boxVL4)
    shapes(LayerPinRecN).insert(boxVL4)
    shapes(LayerPinRecN).insert(pya.Text ("elec2h1", pya.Trans(x0-(r_mh_in)*cos(angle_min_MH/180*pi) - 5.0/dbu,-w/2.0 -  7.5/dbu))).text_size = 0.5/dbu

    #Create the MH Layer
    poly = pya.Path(arc(self.r/dbu, angle_min_MH, angle_max_MH), w_mh).transformed(t).simple_polygon()
    self.cell.shapes(LayermhN).insert(poly)
    boxMH1 = pya.Box(x0+(r_mh_in)*cos(angle_min_MH/180*pi), -w/2.0 -  2.5/dbu, x0 + (r_mh_in)*cos(angle_min_MH/180*pi) + w_mh, y0 +(r_mh_in)*sin(angle_min_MH/180*pi))
    shapes(LayermhN).insert(boxMH1)
    boxMH2 = pya.Box(x0-(r_mh_in)*cos(angle_min_MH/180*pi)  - w_mh, -w/2.0 -  2.5/dbu, x0 - (r_mh_in)*cos(angle_min_MH/180*pi), y0 +(r_mh_in)*sin(angle_min_MH/180*pi))
    shapes(LayermhN).insert(boxMH2)
    boxMH3 = pya.Box(x0+(r_mh_in)*cos(angle_min_MH/180*pi), -w/2.0 -  12.5/dbu, x0 + (r_mh_in)*cos(angle_min_MH/180*pi) + 10/dbu, -w/2.0 -  2.5/dbu)
    shapes(LayermhN).insert(boxMH3)
    boxMH4 = pya.Box(x0-(r_mh_in)*cos(angle_min_MH/180*pi)- 10/dbu, -w/2.0 -  12.5/dbu, x0 - (r_mh_in)*cos(angle_min_MH/180*pi), -w/2.0 -  2.5/dbu)
    shapes(LayermhN).insert(boxMH4)
    
    # Create the pins, as short paths:
    pin_length = 200 # database units, = 0.2 microns
    
    shapes(LayerPinRecN).insert(pya.Path([pya.Point(x0 - (w_Si3 / 2 + taper_length)- pin_length/2, 0),
                                          pya.Point(x0 - (w_Si3 / 2 + taper_length) + pin_length/2, 0)], w))
    shapes(LayerPinRecN).insert(pya.Text("opt1", pya.Trans(x0 - (w_Si3 / 2 + taper_length), 0))).text_size = 0.5/dbu

    shapes(LayerPinRecN).insert(pya.Path([pya.Point(x0 + (w_Si3 / 2 + taper_length)-pin_length/2, 0),
                                          pya.Point(x0 + (w_Si3 / 2 + taper_length) + pin_length/2, 0)], w))
    shapes(LayerPinRecN).insert(pya.Text("opt2", pya.Trans(x0 + (w_Si3 / 2 + taper_length), 0))).text_size = 0.5/dbu

    shapes(LayerPinRecN).insert(pya.Path([pya.Point(x0 - (w_Si3 / 2 + taper_length)- pin_length/2, y_offset),
                                          pya.Point(x0 - (w_Si3 / 2 + taper_length)+ pin_length/2, y_offset)], w))
    shapes(LayerPinRecN).insert(pya.Text("opt3", pya.Trans(x0 - (w_Si3 / 2 + taper_length), y_offset))).text_size = 0.5/dbu

    shapes(LayerPinRecN).insert(pya.Path([pya.Point(x0 + (w_Si3 / 2 + taper_length)-pin_length/2, y_offset),
                                          pya.Point(x0 + (w_Si3 / 2 + taper_length)+ pin_length/2, y_offset)], w))
    shapes(LayerPinRecN).insert(pya.Text("opt4", pya.Trans(x0 + (w_Si3 / 2 + taper_length), y_offset))).text_size = 0.5/dbu

    # Create the device recognition layer
    shapes(LayerDevRecN).insert(pya.Box(x0 - (w_Si3 / 2 + taper_length), -w/2.0 -  12.5/dbu, x0 + (w_Si3 / 2 + taper_length), y0 + r_m1_out + w_m1_out+h_via ))

    # Compact model information
    shape = shapes(LayerDevRecN).insert(pya.Text('Lumerical_INTERCONNECT_library=Design kits/GSiP', \
      pya.Trans(0, 0))).text_size = 0.3/dbu
    shapes(LayerDevRecN).insert(pya.Text ('Lumerical_INTERCONNECT_component=Ring_Filter_DB', \
      pya.Trans(0, w*2))).text_size = 0.3/dbu
    shapes(LayerDevRecN).insert(pya.Text \
      ('Spice_param:radius=%.3fu wg_width=%.3fu gap=%.3fu gap_monitor=%.3fu' %\
      (self.r, self.w, self.g, self.gmon), \
      pya.Trans(0, -w*2) ) ).text_size = 0.3/dbu
    
    # Add a polygon text description
    from ..utils import layout_pgtext
    if self.textpolygon:
      layout_pgtext(self.cell, self.textl, self.w, self.r+self.w, "%.3f-%g" % ( self.r, self.g), 1)

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
    self.param("r_s", self.TypeDouble, "Radius of Center Support (um)", default = 2)
    self.param("e", self.TypeDouble, "Etch Distance (Added to Support, um)", default = 3)
    self.param("layerSi", self.TypeLayer, "Silicon Layer", default = _globals.TECHNOLOGY['LayerSi'])
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
    from ..utils import arc
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
    r_s = self.r_s/dbu
    e = self.e/dbu
    LayerSiN = ly.layer(self.layerSi)
    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)
    LayerTextN = ly.layer(_globals.TECHNOLOGY['LayerText'])

    a_r = pi*30/180
    a_p = (n-1)*a/2+(m+r_h)/cos(a_r)

    # Create Photonic Crystal Ring Resonator
    poly = pya.Polygon([pya.Point(a_p*sin(a_r),a_p*cos(a_r)),
                        pya.Point(a_p,0),
                        pya.Point(a_p*sin(a_r),-a_p*cos(a_r)),
                        pya.Point(-a_p*sin(a_r),-a_p*cos(a_r)),
                        pya.Point(-a_p,0),
                        pya.Point(-a_p*sin(a_r),a_p*cos(a_r))])

    # Create Photonic Crystal
    for i in range(0,ceil(n/2)):
      for j in range(0, n-i):
        x = -a*(n-1)/2 + j*a + i*a/2
        y = i*a*cos(a_r)
        if(sqrt(x*x+y*y)>(r_s+e)):
          if(i==0):
            hole = pya.Polygon(arc(r_h, 0, 360)).transformed(pya.Trans(x, 0)).get_points()
            poly.insert_hole(pya.Polygon(arc(r_h, 0, 360)).transformed(pya.Trans(x, 0)).get_points())
          else:
            poly.insert_hole(pya.Polygon(arc(r_h, 0, 360)).transformed(pya.Trans(x, y)).get_points())
            poly.insert_hole(pya.Polygon(arc(r_h, 0, 360)).transformed(pya.Trans(x, -y)).get_points())
            
    shapes(LayerSiN).insert(poly)

    # Create Area Around Resonator
    gw = 2.0/dbu
    ew = 5.0/dbu
    
    poly = pya.Polygon([pya.Point(a_p+gw/cos(a_r)-(a_p*cos(a_r)+g-gw)*tan(a_r), (a_p*cos(a_r)+g-gw)),
                        pya.Point(a_p+gw/cos(a_r),0),
                        pya.Point(a_p+gw/cos(a_r)-(a_p*cos(a_r)+g-gw)*tan(a_r),-(a_p*cos(a_r)+g-gw)),
                        pya.Point(a_p+(gw+ew)/cos(a_r)-(a_p*cos(a_r)+g-gw)*tan(a_r),-(a_p*cos(a_r)+g-gw)),
                        pya.Point(a_p+(gw+ew)/cos(a_r),0),
                        pya.Point(a_p+(gw+ew)/cos(a_r)-(a_p*cos(a_r)+g-gw)*tan(a_r), (a_p*cos(a_r)+g-gw))])
            
    shapes(LayerSiN).insert(poly)
    shapes(LayerSiN).insert(poly.transform(pya.Trans(2, False, pya.Point(0,0))))

    y = a_p*cos(a_r)+g+0.5/dbu+gw
    poly = pya.Polygon([pya.Point(a_p+(gw+ew)/cos(a_r)-y*tan(a_r), y),
                        pya.Point(-(a_p+(gw+ew)/cos(a_r)-y*tan(a_r)), y),
                        pya.Point(-(a_p+(gw+ew)/cos(a_r))*sin(a_r), a_p*cos(a_r)+gw+ew),
                        pya.Point((a_p+(gw+ew)/cos(a_r))*sin(a_r), a_p*cos(a_r)+gw+ew)])
    
    shapes(LayerSiN).insert(poly)
    shapes(LayerSiN).insert(poly.transform(pya.Trans(0, True, pya.Point(0,0))))

    
    poly = pya.Polygon([pya.Point(a_p*sin(a_r),a_p*cos(a_r)+g),
                        pya.Point(a_p*sin(a_r)+10/dbu,a_p*cos(a_r)+g),
                        pya.Point(a_p+(gw+ew)/cos(a_r),a_p*cos(a_r)+g),
                        pya.Point(a_p+(gw+ew)/cos(a_r),a_p*cos(a_r)+g+0.5/dbu),
                        pya.Point(a_p*sin(a_r)+10/dbu,a_p*cos(a_r)+g+0.5/dbu),
                        pya.Point(a_p*sin(a_r),a_p*cos(a_r)+g+0.275/dbu),
                        pya.Point(-(a_p*sin(a_r)),a_p*cos(a_r)+g+0.275/dbu),
                        pya.Point(-(a_p*sin(a_r)+10/dbu),a_p*cos(a_r)+g+0.5/dbu),
                        pya.Point(-(a_p+(gw+ew)/cos(a_r)),a_p*cos(a_r)+g+0.5/dbu),
                        pya.Point(-(a_p+(gw+ew)/cos(a_r)),a_p*cos(a_r)+g),
                        pya.Point(-(a_p*sin(a_r)+10/dbu),a_p*cos(a_r)+g),
                        pya.Point(-(a_p*sin(a_r)),a_p*cos(a_r)+g)])
    
    shapes(LayerSiN).insert(poly)
    shapes(LayerSiN).insert(poly.transformed(pya.Trans(0, True, pya.Point(0,0))))
    
    poly = pya.Polygon([pya.Point(a_p+(gw+ew)/cos(a_r),a_p*cos(a_r)+gw+ew),
                        pya.Point(-(a_p+(gw+ew)/cos(a_r)),a_p*cos(a_r)+gw+ew),
                        pya.Point(-(a_p+(gw+ew)/cos(a_r)),-(a_p*cos(a_r)+gw+ew)),
                        pya.Point(a_p+(gw+ew)/cos(a_r),-(a_p*cos(a_r)+gw+ew))])
    shapes(LayerDevRecN).insert(poly)
    
    # Pins on the coupler:
    pin_length = 200

    t = pya.Trans(-(a_p+(gw+ew)/cos(a_r)),a_p*cos(a_r)+g+0.5/dbu/2)
    shapes(LayerPinRecN).insert(pya.Path([pya.Point(-pin_length/2, 0), pya.Point(pin_length/2, 0)], 0.5/dbu).transformed(t))
    shapes(LayerPinRecN).insert(pya.Text("pin1", t)).text_size = 0.4/dbu

    t = pya.Trans(a_p+(gw+ew)/cos(a_r),a_p*cos(a_r)+g+0.5/dbu/2)
    shapes(LayerPinRecN).insert(pya.Path([pya.Point(-pin_length/2, 0), pya.Point(pin_length/2, 0)], 0.5/dbu).transformed(t))
    shapes(LayerPinRecN).insert(pya.Text("pin2", t)).text_size = 0.4/dbu
    
    t = pya.Trans(-(a_p+(gw+ew)/cos(a_r)),-(a_p*cos(a_r)+g+0.5/dbu/2))
    shapes(LayerPinRecN).insert(pya.Path([pya.Point(-pin_length/2, 0), pya.Point(pin_length/2, 0)], 0.5/dbu).transformed(t))
    shapes(LayerPinRecN).insert(pya.Text("pin3", t)).text_size = 0.4/dbu

    t = pya.Trans(a_p+(gw+ew)/cos(a_r),-(a_p*cos(a_r)+g+0.5/dbu/2))
    shapes(LayerPinRecN).insert(pya.Path([pya.Point(-pin_length/2, 0), pya.Point(pin_length/2, 0)], 0.5/dbu).transformed(t))
    shapes(LayerPinRecN).insert(pya.Text("pin4", t)).text_size = 0.4/dbu

class GSiP(pya.Library):
  def __init__(self):
    print("Initializing SiEPIC GSiP Library.")

    self.description = ""

    import os
    self.layout().read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "SiEPIC-GSiP.gds"))
    [self.layout().rename_cell(i, self.layout().cell_name(i).replace('_', ' ')) for i in range(0, self.layout().cells())]
    
    self.layout().register_pcell("Double-bus Ring Modulator", Ring_Modulator_DB())
    self.layout().register_pcell("Double-bus Ring Filter", Ring_Filter_DB())
    self.layout().register_pcell("Photonic Crystal Hexagonal Ring Resonator", PC_Hex_Ring_Resonator_Edge())
    
    self.register("SiEPIC GSiP Library")