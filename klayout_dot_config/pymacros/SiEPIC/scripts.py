import pya

def waveguide_from_path(params = None, cell = None):
  from . import _globals
  from .utils import select_paths

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
  
  status = _globals.WG_GUI.return_status()
  if status is None and params is None:
    _globals.WG_GUI.show()
  else:
    lv.transaction("waveguide from path")

    if status is False: return
    if params is None: params = _globals.WG_GUI.get_parameters()  
    
    selected_paths = select_paths(_globals.TECHNOLOGY['LayerSi'], cell)
    selection = []
  
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
      if not path.radius_check(params['radius']):
        warning.setText("Warning: One of the waveguide segments has insufficient length to accommodate the desired bend radius.")
        warning.setInformativeText("Do you want to Proceed?")
        if(warning.exec_() == pya.QMessageBox.Cancel):
          return
      
      path.snap(_globals.NET.refresh().pins)
      path = pya.DPath(path.get_dpoints(), path.width) * _globals.TECHNOLOGY['dbu']
      path.width = path.width * _globals.TECHNOLOGY['dbu']
      pcell = ly.create_cell("Waveguide", "SiEPIC Common Library", { "path": path,
                                                                     "radius": params['radius'],
                                                                     "width": params['width'],
                                                                     "adiab": params['adiabatic'],
                                                                     "bezier": params['bezier'],
                                                                     "layers": [wg['layer'] for wg in params['wgs']] + [_globals.TECHNOLOGY['LayerDevRec']],
                                                                     "widths": [wg['width'] for wg in params['wgs']] + [3*params['width']],
                                                                     "offsets": [wg['offset'] for wg in params['wgs']] + [0]} )
      selection.append(pya.ObjectInstPath())
      selection[-1].top = obj.top
      selection[-1].append_path(pya.InstElement.new(cell.insert(pya.CellInstArray(pcell.cell_index(), pya.Trans(0, 0)))))
      
      obj.shape.delete()
    
    lv.clear_object_selection()
    lv.object_selection = selection
    lv.commit()
    
def waveguide_to_path(cell = None):
  from . import _globals
  from .utils import select_waveguides
  
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
    
  lv.transaction("waveguide to path")
  
  waveguides = select_waveguides(cell)
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
    
    obj.inst().delete()

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
  
def calibreDRC(params = None, cell = None):
  from . import _globals

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
  
  status = _globals.DRC_GUI.return_status()
  if status is None and params is None:
    _globals.DRC_GUI.show()
  else:
    if status is False: return
    if params is None: params = _globals.DRC_GUI.get_parameters()
    
    if any(value == '' for key, value in params.items()):
      raise Exception("Missing information")

    lv.transaction("calibre drc")
    progress = pya.RelativeProgress("Calibre DRC", 100)
    progress.value = 0
    pya.Application.instance().main_window().update()
    # Python version
    import sys, os, pipes, codecs
    if sys.platform.startswith('win'):
      local_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Temp')
    else:
      local_path = "/tmp"
    local_file = os.path.basename(lv.active_cellview().filename())
    local_pathfile = os.path.join(local_path, local_file)
    
    remote_path = "/tmp"
    
    results_file = os.path.basename(local_pathfile) + ".rve"
    results_pathfile = os.path.join(os.path.dirname(local_pathfile), results_file)
    progress.format = "Saving temporary layout"
    tmp_ly = ly.dup()
    [cell.flatten(True) for cell in tmp_ly.each_cell()]
    opts = pya.SaveLayoutOptions()
    opts.format = "GDS2"
    tmp_ly.write(local_pathfile, opts)
    progress.value = 25
    pya.Application.instance().main_window().update()
    with codecs.open(os.path.join(local_path, 'run_calibre'), 'w', encoding="utf-8") as file:
      cal_script  = '#!/bin/tcsh \n'
      cal_script += 'source %s \n' % params['calibre']
      cal_script += 'setenv SIEPIC_IME_PDK %s \n' % params['pdk']
      cal_script += '$MGC_HOME/bin/calibre -drc -hier -turbo -nowait drc.cal \n'
      file.write(cal_script)

    with codecs.open(os.path.join(local_path, 'drc.cal'), 'w', encoding="utf-8") as file:
      cal_deck  = 'LAYOUT PATH  "%s"\n' % os.path.basename(local_pathfile)
      cal_deck += 'LAYOUT PRIMARY "%s"\n' % cell.name
      cal_deck += 'LAYOUT SYSTEM GDSII\n'
      cal_deck += 'DRC RESULTS DATABASE "drc.rve" ASCII\n'
      cal_deck += 'DRC MAXIMUM RESULTS ALL\n'
      cal_deck += 'DRC MAXIMUM VERTEX 4096\n'
      cal_deck += 'DRC CELL NAME YES CELL SPACE XFORM\n'
      cal_deck += 'VIRTUAL CONNECT COLON NO\n'
      cal_deck += 'VIRTUAL CONNECT REPORT NO\n'
      cal_deck += 'DRC ICSTATION YES\n'
      cal_deck += 'INCLUDE "%s/calibre_rule_decks/CMC_SiEPIC_IMESP.drc.cal"\n' % params['pdk']
      file.write(cal_deck)

    version = sys.version
    if version.find("2.") > -1:
      import commands
      pya.Application.instance().main_window().update()
      progress.format = "Uploading layout and scripts"
      out = cmd('cd "%s" && scp -i C:/Users/bpoul/.ssh/drc -P%s "%s" %s:%s' % (os.path.dirname(local_pathfile), params['port'], os.path.basename(local_pathfile), params['url'], remote_path))
      out = cmd('cd "%s" && scp -i C:/Users/bpoul/.ssh/drc -P%s %s %s:%s' % (local_path, params['port'], 'run_calibre', params['url'], remote_path))
      out = cmd('cd "%s" && scp -i C:/Users/bpoul/.ssh/drc -P%s %s %s:%s' % (local_path, params['port'], 'drc.cal', params['url'], remote_path))
      progress.value = 50
      progress.format = "Checking layout for errors"
      pya.Application.instance().main_window().update()
      out = cmd('ssh -i C:/Users/bpoul/.ssh/drc -p%s %s "%s"' % (params['port'], params['url'], "cd " + remote_path +" && source run_calibre"))
      progress.value = 75
      progress.format = "Downloading Errors"
      pya.Application.instance().main_window().update()
      out = cmd('cd "%s" && scp -i C:/Users/bpoul/.ssh/drc -P%s %s:%s %s' % (os.path.dirname(local_pathfile), params['port'], params['url'], remote_path + "/drc.rve", results_file))
      progress.value = 100
      pya.Application.instance().main_window().update()
    elif version.find("3.") > -1:
      import subprocess
      cmd = subprocess.check_output
      progress.format = "Uploading layout and scripts"
      pya.Application.instance().main_window().update()
      out = cmd('cd "%s" && scp -i %s -P%s "%s" %s:%s' % (os.path.dirname(local_pathfile), params['identity'], params['port'], os.path.basename(local_pathfile), params['url'], remote_path), shell=True)
      out = cmd('cd "%s" && scp -i %s -P%s %s %s:%s' % (local_path, params['identity'], params['port'], 'run_calibre', params['url'], remote_path), shell=True)
      out = cmd('cd "%s" && scp -i %s -P%s %s %s:%s' % (local_path, params['identity'], params['port'], 'drc.cal', params['url'], remote_path), shell=True)
      progress.value = 50
      progress.format = "Checking layout for errors"
      pya.Application.instance().main_window().update()
      out = cmd('ssh -i %s -p%s %s "%s"' % (params['identity'], params['port'], params['url'], "cd " + remote_path +" && source run_calibre"), shell=True)
      progress.value = 75
      progress.format = "Downloading Errors"
      pya.Application.instance().main_window().update()
      out = cmd('cd "%s" && scp -i %s -P%s %s:%s %s' % (os.path.dirname(local_pathfile), params['identity'], params['port'], params['url'], remote_path + "/drc.rve", results_file), shell=True)
      progress.value = 100
      pya.Application.instance().main_window().update()
      
    progress._destroy()
    if os.path.exists(results_pathfile):
      rdb_i = lv.create_rdb("Calibre Verification")
      rdb = lv.rdb(rdb_i)
      rdb.load (results_pathfile)
      rdb.top_cell_name = cell.name
      rdb_cell = rdb.create_cell(cell.name)
      lv.show_rdb(rdb_i, lv.active_cellview().cell_index)
    else:
      pya.MessageBox.warning("Errors", "Something failed during the server Calibre DRC check.",  pya.MessageBox.Ok)

    lv.commit()
    
def auto_coord_extract():
  from . import _globals
  def gen_ui():
    global wdg
    if 'wdg' in globals():
      if wdg is not None and not wdg.destroyed():
        wdg.destroy()
    global wtext
  
    def button_clicked(checked):
      """ Event handler: "OK" button clicked """
      wdg.destroy()
  
    wdg = pya.QDialog(pya.Application.instance().main_window())
  
    wdg.setAttribute(pya.Qt.WA_DeleteOnClose)
    wdg.setWindowTitle("SiEPIC-EBeam-PDK: Automated measurement coordinate extraction")
  
    wdg.resize(1000, 500)
    wdg.move(1, 1)
  
    grid = pya.QGridLayout(wdg)
  
    windowlabel1 = pya.QLabel(wdg)
    windowlabel1.setText("output:")
    wtext = pya.QTextEdit(wdg)
    wtext.enabled = True
    wtext.setText('')
  
    ok = pya.QPushButton("OK", wdg)
    ok.clicked(button_clicked)   # attach the event handler
    netlist = pya.QPushButton("Save", wdg) # not implemented
  
    grid.addWidget(windowlabel1, 0, 0, 1, 3)
    grid.addWidget(wtext, 1, 1, 3, 3)
    grid.addWidget(netlist, 4, 2)
    grid.addWidget(ok, 4, 3)
  
    grid.setRowStretch(3, 1)
    grid.setColumnStretch(1, 1)
  
    wdg.show()
  
  # Create a GUI for the output:
  gen_ui()
  wtext.insertHtml('<br>* Automated measurement coordinates:<br><br>')
  
  # Find the automated measurement coordinates:
  from .utils import find_automated_measurement_labels
  cell = pya.Application.instance().main_window().current_view().active_cellview().cell
  t = find_automated_measurement_labels(cell, cell.layout().layer(_globals.TECHNOLOGY['LayerText']))
  wtext.insertHtml (t)
  
def layout_check():
  print("layout_check")
  
def text_netlist_check():
  print("text_netlist_check")