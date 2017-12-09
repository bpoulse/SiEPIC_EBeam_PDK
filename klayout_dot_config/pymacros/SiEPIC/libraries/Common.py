import pya
from .. import _globals

class Waveguide(pya.PCellDeclarationHelper):

  def __init__(self):
    # Important: initialize the super class
    super(Waveguide, self).__init__()
    # declare the parameters
    self.param("path", self.TypeShape, "Path", default = pya.Path([pya.Point(0,0), pya.Point(10,0), pya.Point(10,10)], 0.5))
    self.param("radius", self.TypeDouble, "Radius", default = 5)
    self.param("width", self.TypeDouble, "Width", default = 0.5)
    self.param("adiab", self.TypeBoolean, "Adiabatic", default = False)
    self.param("bezier", self.TypeDouble, "Bezier Parameter", default = 0.35)
    self.param("layers", self.TypeList, "Layers", default = [_globals.TECHNOLOGY['LayerSi']])
    self.param("widths", self.TypeList, "Widths", default =  [0.5])
    self.param("offsets", self.TypeList, "Offsets", default = [0])
    
  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "Waveguide_%s" % self.path
  
  def coerce_parameters_impl(self):
    pass

  def can_create_from_shape(self, layout, shape, layer):
    return shape.is_path()

  def transformation_from_shape(self, layout, shape, layer):
    return Trans(0,0)

  def parameters_from_shape(self, layout, shape, layer):
    self._param_values = []
    for pd in self._param_decls:
      self._param_values.append(pd.default)
    return self._param_values
        
  def produce_impl(self):

    from ..utils import arc, arc_bezier, angle_vector, angle_b_vectors, inner_angle_b_vectors
    from math import cos, sin, pi, sqrt

    dbu = self.layout.dbu
    path = self.path*(1/dbu)
    if not (len(self.layers)==len(self.widths) and len(self.layers)==len(self.offsets) and len(self.offsets)==len(self.widths)):
      raise Exception("There must be an equal number of layers, widths and offsets")
    path.remove_colinear_points()
    for i in range(0, len(self.layers)):
      
      if isinstance(self.layers[i], str):
        layer = self.layers[i].split('/')
        layer = self.layout.layer(pya.LayerInfo(int(layer[0]), int(layer[1])))
      else:
        layer = self.layout.layer(self.layers[i])

      width = float(self.widths[i])/dbu
      offset = float(self.offsets[i])/dbu
      #radius = self.radius/dbu + offset
      
      tpath = path.translate_from_center(offset)
      
      pts = tpath.get_points()
      wg_pts = [pts[0]]
      for i in range(1,len(pts)-1):
        turn = ((angle_b_vectors(pts[i]-pts[i-1],pts[i+1]-pts[i])+90)%360-90)/90
        radius = (self.radius/dbu + offset) if turn > 0 else (self.radius/dbu - offset)

        pt_radius = radius
        dis = pts[i-1].distance(pts[i])
        if (dis < pt_radius):
          pt_radius = dis if i==1 else dis/2  
        dis = pts[i].distance(pts[i+1])
        if (dis  < pt_radius):
          pt_radius = dis if i==len(pts)-2 else dis/2

        if(self.adiab):
          arc_pts = [pya.Point(-pt_radius, pt_radius) + pt for pt in arc_bezier(pt_radius, 270, 270 + inner_angle_b_vectors(pts[i-1]-pts[i], pts[i+1]-pts[i]), self.bezier)]
        else:
          arc_pts = [pya.Point(-pt_radius, pt_radius) + pt for pt in arc(pt_radius, 270, 270 + inner_angle_b_vectors(pts[i-1]-pts[i], pts[i+1]-pts[i]))]
        angle = angle_vector(pts[i]-pts[i-1])/90
        
        wg_pts += pya.Path(arc_pts, width).transformed(pya.Trans(angle, turn < 0, pts[i])).get_points()

      wg_pts.append(pts[-1])
      self.cell.shapes(layer).insert(pya.Path(wg_pts, width).simple_polygon())

    pts = path.get_points()
    LayerPinRecN = self.layout.layer(_globals.TECHNOLOGY['LayerPinRec'])
    
    t = pya.Trans(angle_vector(pts[0]-pts[1])/90, False, pts[0])
    self.cell.shapes(LayerPinRecN).insert(pya.Path([pya.Point(-100, 0), pya.Point(100, 0)], self.width/dbu).transformed(t))
    self.cell.shapes(LayerPinRecN).insert(pya.Text("pin1", t)).text_size = 0.4/dbu
    
    t = pya.Trans(angle_vector(pts[-1]-pts[-2])/90, False, pts[-1])
    self.cell.shapes(LayerPinRecN).insert(pya.Path([pya.Point(-100, 0), pya.Point(100, 0)], self.width/dbu).transformed(t))
    self.cell.shapes(LayerPinRecN).insert(pya.Text("pin2", t)).text_size = 0.4/dbu

    self.cell.shapes(self.layout.guiding_shape_layer()).insert(pya.Path(path.get_points(), path.width))
    
class Ring(pya.PCellDeclarationHelper):
  def __init__(self):
    # Important: initialize the super class
    super(Ring, self).__init__()
    # declare the parameters
    self.param("width", self.TypeDouble, "Width", default = 0.5)
    self.param("radius", self.TypeDouble, "Radius", default = 5)
    self.param("layer", self.TypeLayer, "Layer", default = _globals.TECHNOLOGY['LayerSi'])
    
  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "Ring_%s" % self.radius
  
  def coerce_parameters_impl(self):
    pass
        
  def produce_impl(self):
    from ..utils import arc
    
    dbu = self.layout.dbu
    
    layer = self.layout.layer(self.layer)
    radius = self.radius/dbu
    width = self.width/dbu
    
    poly = pya.Polygon(arc(radius+width/2, 0, 360))
    hole = pya.Polygon(arc(radius-width/2, 0, 360))
    poly.insert_hole(hole.get_points())
    self.cell.shapes(layer).insert(poly)

class LumericalINTERCONNECT_Laser(pya.PCellDeclarationHelper):
  """
  The PCell declaration for the LumericalINTERCONNECT Optical Network Analyzer.
  This configures the swept tunable laser
  
  Ultimately want to generate Spice output such as:
  
  .ona input_unit=wavelength input_parameter=center_and_range center=1550e-9
  + range=100e-9 start=3 stop=4 number_of_points=1000 orthogonal_identifier=1
  + label=TE peak_analysis=disable number_of_peaks=8 peak_at_maximum=9
  + peak_threshold=0 peak_excursion=11 pit_excursion=12 fwhm_excursion=13
  + minimum_loss=14 sensitivity=-200 analysis_type=scattering_data
  + multithreading=automatic number_of_threads=1 input(1)=X_GC1,opt_fiber
  + output=X_GC2,opt_fiber

  
  """
  def __init__(self):
    # Important: initialize the super class
    super(LumericalINTERCONNECT_Laser, self).__init__()
    # declare the parameters
    self.param("wavelength_start", self.TypeDouble, "Start Wavelength (nm)", default = 1500)
    self.param("wavelength_stop", self.TypeDouble, "Stop Wavelength (nm)", default = 1600)
    self.param("npoints", self.TypeInt, "Number of points", default = 2000)     
    self.param("orthogonal_identifier", self.TypeInt, "Orthogonal identifier (1=TE, 2=TM)", default = 1)     
    self.param("ignoreOpticalIOs", self.TypeInt, "Ignore optical IOs in simulations (1=Ignore, 0=Include)", default = 0)
    self.param("s", self.TypeShape, "", default = pya.DPoint(0, 0))

  def can_create_from_shape_impl(self):
    return False
    
  def produce_impl(self):
    ly = self.layout
    shapes = self.cell.shapes
    dbu = self.layout.dbu
    
    LayerINTERCONNECT = ly.layer(_globals.TECHNOLOGY['LayerLumerical'])

    # Draw the laser
    width = 60/dbu
    height = 40/dbu
    shapes(LayerINTERCONNECT).insert(pya.Box(-width/2, -height/2, width/2, height/2))
    
    shapes(LayerINTERCONNECT).insert(pya.Text("Tunable Laser", pya.Trans(-width/2+3/dbu, height/2-4/dbu))).text_size = 1.5/dbu
    shapes(LayerINTERCONNECT).insert(pya.Text("Wavelength range: %4.3f - %4.3f nm" % (self.wavelength_start, self.wavelength_stop), pya.Trans(-width/2+3/dbu, height/2-8/dbu))).text_size = 1.5/dbu
    shapes(LayerINTERCONNECT).insert(pya.Text ("Number of points: %s" % (self.npoints), pya.Trans(-width/2+3/dbu, height/2-12/dbu))).text_size = 1.5/dbu
    shapes(LayerINTERCONNECT).insert(pya.Text("Ignore optical IOs in simulations: %s" % (self.ignoreOpticalIOs), pya.Trans(-width/2+3/dbu, height/2-16/dbu))).text_size = 1.5/dbu
    # Add a polygon text description
    from ..utils import layout_pgtext
    layout_pgtext(self.cell, _globals.TECHNOLOGY['LayerText'], -width/2*dbu+3, -height/2*dbu+2, "Number of points: %s" % (self.npoints), 2.2)
    layout_pgtext(self.cell, _globals.TECHNOLOGY['LayerText'], -width/2*dbu+3, -height/2*dbu+5, "Wavelength range: %4.3f - %4.3f nm" % (self.wavelength_start, self.wavelength_stop), 2.2)

class LumericalINTERCONNECT_Detector(pya.PCellDeclarationHelper):
  """
  The PCell declaration for the LumericalINTERCONNECT Optical Network Analyzer.
  This configures the detector  
  """
  def __init__(self):
    # Important: initialize the super class
    super(LumericalINTERCONNECT_Detector, self).__init__()
    detector_number = 1
      
    # declare the parameters
    self.param("number", self.TypeInt, "Detector number", default = detector_number)     
    self.param("s", self.TypeShape, "", default = pya.DPoint(0, 0))

  def can_create_from_shape_impl(self):
    return False

  def coerce_parameters_impl(self):
    pass
           
  def produce_impl(self):
    ly = self.layout
    shapes = self.cell.shapes
    dbu = self.layout.dbu
    
    LayerINTERCONNECT = ly.layer(_globals.TECHNOLOGY['LayerLumerical'])

    # Draw the outline
    width = 60/dbu
    height = 40/dbu
    shapes(LayerINTERCONNECT).insert(pya.Box(-width/2, -height/2, width/2, height/2))

    shapes(LayerINTERCONNECT).insert(pya.Text("Detector", pya.Trans(-width/2+3/dbu, height/2-4/dbu))).text_size = 1.5/dbu
    shapes(LayerINTERCONNECT).insert(pya.Text("Detector Number: %s" % (self.number), pya.Trans(-width/2+3/dbu, height/2-8/dbu))).text_size = 1.5/dbu
    shapes(LayerINTERCONNECT).insert(pya.Text("LumericalINTERCONNECT_Detector %s" % (self.number), pya.Trans(0,0))).text_size = 0.1/dbu

    # Add a polygon text description
    from ..utils import layout_pgtext
    layout_pgtext(self.cell, _globals.TECHNOLOGY['LayerText'], -width/2*dbu+3, -height/2*dbu+2, "Number: %s" % (self.number), 2.2)

class Common(pya.Library):
  def __init__(self):
    print("Initializing SiEPIC Common Library.")
    
    self.description = ""

    import os
    self.layout().read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "SiEPIC-Common.gds"))
    [self.layout().rename_cell(i, self.layout().cell_name(i).replace('_', ' ')) for i in range(0, self.layout().cells())]
    
    self.layout().register_pcell("Lumerical INTERCONNECT Laser", LumericalINTERCONNECT_Laser())
    self.layout().register_pcell("Lumerical INTERCONNECT Detector", LumericalINTERCONNECT_Detector())
    self.layout().register_pcell("Waveguide", Waveguide())
    self.layout().register_pcell("Ring", Ring())
    
    self.register("SiEPIC Common Library")