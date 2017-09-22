import pya

#Keeps SiEPIC global variables and libraries consistent with technology of current layout
#Triggered when new layout is created or the current view changes
#NOT yet implemented to update with the "select technology" button
def load_technology():
  from . import _globals
  view = pya.Application.instance().main_window().current_view()
  if view is not None:
    view = view.active_cellview()
    if view is not None:
      tech = view.technology
      if tech is '': tech = 'default'
      _globals.TECHNOLOGY = _globals.TECHNOLOGIES[tech]
      _globals.TECHNOLOGY['dbu'] = view.layout().dbu
      from importlib import import_module
      if not any('Common' in library for library in pya.Library.library_names()):
        try:
          getattr(import_module('.libraries.Common', 'SiEPIC'), 'Common')()
        except Exception as e:
         print(e)

      if not any([_globals.TECHNOLOGY['library'] in library for library in pya.Library.library_names()]):
        try:
          getattr(import_module('.libraries.%s' % (_globals.TECHNOLOGY['library']), 'SiEPIC'), _globals.TECHNOLOGY['library'])()
        except Exception as e:
          print(e)

#Define an Enumeration type for Python
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

#Return all selected paths. If nothing is selected, select paths automatically
def select_paths(lyr, cell = None):
  lv = pya.Application.instance().main_window().current_view()
  if lv == None:
    raise Exception("No view selected")

  if cell is None:
    ly = lv.active_cellview().layout() 
    if ly == None:
      raise Exception("No active layout")
    cell = lv.active_cellview().cell
    if cell == None:
      raise Exception("No active cell")
  else:
    ly = cell.layout()
    
  selection = lv.object_selection
  if selection == []:
    itr = cell.begin_shapes_rec(ly.layer(lyr))
    while not(itr.at_end()):
      if itr.shape().is_path():
        selection.append(pya.ObjectInstPath())
        selection[-1].layer = ly.layer(lyr)
        selection[-1].shape = itr.shape()
        selection[-1].top = cell.cell_index()
        selection[-1].cv_index = 0
      itr.next()
    lv.object_selection = selection
  else:
    lv.object_selection = [o for o in selection if (not o.is_cell_inst()) and o.shape.is_path()]
    
  return lv.object_selection
  
#Return all selected waveguides. If nothing is selected, select waveguides automatically
def select_waveguides(cell = None):
  lv = pya.Application.instance().main_window().current_view()
  if lv == None:
    raise Exception("No view selected")

  if cell is None:
    ly = lv.active_cellview().layout() 
    if ly == None:
      raise Exception("No active layout")
    cell = lv.active_cellview().cell
    if cell == None:
      raise Exception("No active cell")
  else:
    ly = cell.layout()

  selection = lv.object_selection
  if selection == []:
    for instance in cell.each_inst():
      if instance.cell.basic_name() == "Waveguide":
        selection.append(pya.ObjectInstPath())
        selection[-1].top = cell.cell_index()
        selection[-1].append_path(pya.InstElement.new(instance))
    lv.object_selection = selection
  else:
    lv.object_selection = [o for o in selection if o.is_cell_inst() and o.inst().cell.basic_name() == "Waveguide"]
    
  return lv.object_selection
  
#Find the angle between two vectors (not necessarily the smaller angle)
def angle_b_vectors(u, v):
  from math import atan2, pi
  return (atan2(v.y, v.x)-atan2(u.y, u.x))/pi*180

#Find the angle between two vectors (will always be the smaller angle)
def inner_angle_b_vectors(u, v):
  from math import acos, pi
  return acos((u.x*v.x+u.y*v.y)/(u.abs()*v.abs()))/pi*180

#Find the angle of a vector
def angle_vector(u):
  from math import atan2, pi
  return (atan2(u.y,u.x))/pi*180

#Truncate the angle
def angle_trunc(a, trunc):
  return ((a%trunc)+trunc)%trunc

# Calculate the recommended number of points in a circle, based on 
# http://stackoverflow.com/questions/11774038/how-to-render-a-circle-with-as-few-vertices-as-possible
def points_per_circle(radius):
  from math import acos, pi, ceil
  from . import _globals
  err = 1e3*_globals.TECHNOLOGY['dbu']/2
  return int(ceil(2*pi/acos(2 * (1 - err / radius)**2 - 1))) if radius > 0.1 else 100

#Create an arc spanning from start to stop in degrees
def arc(radius, start, stop):
  from math import pi, cos, sin
  start = start*pi/180
  stop = stop*pi/180

  da = 2*pi/points_per_circle(radius)
  n = int(abs(stop-start)/da)
  if n == 0: n = 1
  return [pya.Point.from_dpoint(pya.DPoint(radius*cos(start+i*da), radius*sin(start+i*da))) for i in range(0, n+1) ]

#Create a bezier curve. While there are parameters for start and stop in degrees, this is currently only implemented for 90 degree bends
def arc_bezier(radius, start, stop, bezier):
  from math import sin, cos, pi
  N=100
  L = radius  # effective bend radius / Length of the bend
  diff = 1/(N-1)
  xp=[0, (1-bezier)*L, L, L]
  yp=[0, 0, bezier*L, L]
  xA = xp[3] - 3*xp[2] + 3*xp[1] - xp[0]
  xB = 3*xp[2] - 6*xp[1] + 3*xp[0]
  xC = 3*xp[1] - 3*xp[0]
  xD = xp[0]
  yA = yp[3] - 3*yp[2] + 3*yp[1] - yp[0]
  yB = 3*yp[2] - 6*yp[1] + 3*yp[0]
  yC = 3*yp[1] - 3*yp[0]
  yD = yp[0]
  
  pts = [pya.Point(-L,0) + pya.Point(xD, yD)]
  for i in range(1, N):
    t = i*diff
    pts.append(pya.Point(-L,0) + pya.Point(t**3*xA + t**2*xB + t*xC + xD, t**3*yA + t**2*yB + t*yC + yD))
  return pts

#Take a list of points and create a polygon of width 'width' 
def arc_to_waveguide(pts, width):
  return pya.Polygon(translate_from_normal(pts, -width/2) + translate_from_normal(pts, width/2)[::-1])

#Translate each point by its normal a distance 'trans'
def translate_from_normal(pts, trans):
  from math import cos, sin, pi
  d = 1/(len(pts)-1)
  
  a = angle_vector(pts[1]-pts[0])*pi/180 + (pi/2 if trans > 0 else -pi/2)
  tpts = [pts[0] + pya.Point(abs(trans)*cos(a), abs(trans)*sin(a))]
  
  for i in range(1, len(pts)-1):
    dpt = (pts[i+1]-pts[i-1])*(2/d)
    tpts.append(pts[i] + pya.Point(-dpt.y, dpt.x)*(trans/2/dpt.abs()))
    
  a = angle_vector(pts[-1]-pts[-2])*pi/180 + (pi/2 if trans > 0 else -pi/2)
  tpts.append(pts[-1] + pya.Point(abs(trans)*cos(a), abs(trans)*sin(a)))
  
  return tpts

#Check if point c intersects the segment defined by pts a and b
def pt_intersects_segment(a, b, c):
  """ How can you determine a point is between two other points on a line segment?
  http://stackoverflow.com/questions/328107/how-can-you-determine-a-point-is-between-two-other-points-on-a-line-segment
  by Cyrille Ka.  Check if c is between a and b? """
  cross = abs((c.y - a.y) * (b.x - a.x) - (c.x - a.x) * (b.y - a.y))
  if round(cross, 5) != 0 : return False

  dot = (c.x - a.x) * (b.x - a.x) + (c.y - a.y)*(b.y - a.y)
  if dot < 0 : return False
  return False if dot > (b.x - a.x)*(b.x - a.x) + (b.y - a.y)*(b.y - a.y) else True

#Add bubble to a cell
# Example
# cell = pya.Application.instance().main_window().current_view().active_cellview().cell
# layout_pgtext(cell, LayerInfo(10, 0), 0, 0, "test", 1)
def layout_pgtext(cell, layer, x, y, text, mag):
  # for the Text polygon:
  textlib = pya.Library.library_by_name("Basic")
  if textlib == None:
    raise Exception("Unknown lib 'Basic'")

  textpcell_decl = textlib.layout().pcell_declaration("TEXT")
  if textpcell_decl == None:
    raise Exception("Unknown PCell 'TEXT'")
  param = { 
    "text": text, 
    "layer": layer, 
    "mag": mag 
  }
  pv = []
  for p in textpcell_decl.get_parameters():
    if p.name in param:
      pv.append(param[p.name])
    else:
      pv.append(p.default)
  # "fake PCell code" 
  text_cell = cell.layout().create_cell("Temp_text_cell")
  textlayer_index = cell.layout().layer(layer)
  textpcell_decl.produce(cell.layout(), [ textlayer_index ], pv, text_cell)

  # fetch the database parameters
  dbu = cell.layout().dbu
  t = pya.Trans(pya.Trans.R0, x/dbu, y/dbu)
  cell.insert(pya.CellInstArray(text_cell.cell_index(), t))
  # flatten and delete polygon text cell
  cell.flatten(True)
          
try:
  advance_iterator = next
except NameError:
  def advance_iterator(it):
    return it.next()