import pya

def waveguide_from_path():
  from . import _globals
  from .utils import select_paths
  
  lv = pya.Application.instance().main_window().current_view()
  if lv == None:
    raise Exception("No view selected")
  ly = lv.active_cellview().layout() 
  if ly == None:
    raise Exception("No active layout")
  cell = lv.active_cellview().cell
  if cell == None:
    raise Exception("No active cell")
  
  status = _globals.WG_GUI.return_status()
  if status is None:
    _globals.WG_GUI.show()
  else:
    lv.transaction("waveguide from path")
  
    if not status:
      return
    
    selected_paths = select_paths(_globals.TECHNOLOGY['LayerSi'])
    selection = []
    param = _globals.WG_GUI.get_parameters()
  
    warning = pya.QMessageBox()
    warning.setStandardButtons(pya.QMessageBox.Yes | pya.QMessageBox.Cancel)
    warning.setDefaultButton(pya.QMessageBox.Yes)
    for obj in selected_paths:
      path = obj.shape.path
      if not path.is_manhattan():
        warning.setText("Warning: Waveguide segments (first, last) are not Manhattan (vertical, horizontal).")
        warning.setInformativeText("Do you want to Proceed?")
        if(warning.exec_() == pya.QMessageBox.Cancel):
          return
      if not path.radius_check(param['radius']):
        warning.setText("Warning: One of the waveguide segments has insufficient length to accommodate the desired bend radius.")
        warning.setInformativeText("Do you want to Proceed?")
        if(warning.exec_() == pya.QMessageBox.Cancel):
          return
      
      path.snap(_globals.NET.refresh().pins)
      path = pya.DPath(path.get_dpoints(), path.width) * _globals.TECHNOLOGY['dbu']
      path.width = path.width * _globals.TECHNOLOGY['dbu']
      pcell = ly.create_cell("Waveguide", "SiEPIC Common Library", { "path": path,
                                                                     "radius": param['radius'],
                                                                     "width": param['width'],
                                                                     "adiab": param['adiabatic'],
                                                                     "bezier": param['bezier'],
                                                                     "layers": [wg['layer'] for wg in param['wgs']],
                                                                     "widths": [wg['width'] for wg in param['wgs']],
                                                                     "offsets": [wg['offset'] for wg in param['wgs']] } )
      selection.append(pya.ObjectInstPath())
      selection[-1].top = obj.top
      selection[-1].append_path(pya.InstElement.new(cell.insert(pya.CellInstArray(pcell.cell_index(), pya.Trans(0, 0)))))
      
      obj.shape.delete()
    
    lv.clear_object_selection()
    lv.object_selection = selection
    lv.commit()
  
def waveguide_to_path():
  from . import _globals
  from .utils import select_waveguides
  
  lv = pya.Application.instance().main_window().current_view()
  if lv == None:
    raise Exception("No view selected")
  ly = lv.active_cellview().layout() 
  if ly == None:
    raise Exception("No active layout")
  cell = lv.active_cellview().cell
  if cell == None:
    raise Exception("No active cell")
  
  lv.transaction("waveguide to path")
  
  waveguides = select_waveguides()
  selection = []
  for obj in waveguides:
    waveguide = obj.inst()
    path = waveguide.cell.shapes(waveguide.layout().guiding_shape_layer()).each().__next__().path
    path.width = 0.5/_globals.TECHNOLOGY['dbu']
    
    selection.append(pya.ObjectInstPath())
    selection[-1].layer = ly.layer(_globals.TECHNOLOGY['LayerSi'])
    selection[-1].shape = cell.shapes(ly.layer(_globals.TECHNOLOGY['LayerSi'])).insert(path)
    selection[-1].top = obj.top
    selection[-1].cv_index = obj.cv_index
    
    obj.inst().cell.delete()

  lv.clear_object_selection()
  lv.object_selection = selection
  lv.commit()
  
def waveguide_length():
  print("waveguide_length")
  
def waveguide_length_diff():
  print("waveguide_length_diff")

def waveguide_heal():
  print("waveguide_heal")

def auto_route():
  print("auto_route")
  
def snap_component():
  print("snap_component")
  
def compute_area():
  print("compute_area")
  
def calibreDRC():
  print("calibreDRC")
  
def auto_coord_extract():
  print("auto_coord_extract")
  
def layout_check():
  print("layout_check")
  
def text_netlist_check():
  print("text_netlist_check")