from pathlib import Path
root=Path('C:/Projects/Github/Adherent/SYS/Board_STEP_Models')
old=(root/'IOCTRL_Waveshare_ESP32-S3-ETH-8DI-8RO/build_ocp_R1.py').read_text()
imports=old[:old.index('base=box(')]
body='''W,H,T=137.29,105.0,1.6
pcb=box(2,0,0,W-4,H,T)
pcb=BRepAlgoAPI_Fuse(pcb,box(0,2,0,W,H-4,T)).Shape()
for x in (2,W-2):
 for y in (2,H-2): pcb=BRepAlgoAPI_Fuse(pcb,cylinder(x,y,2,T)).Shape()
holes=[(4,4),(W-4,4),(4,H-4),(W-4,H-4)]
for x,y in holes: pcb=cut(pcb,cylinder(x,y,1.6,T))
parts=[('PCB estimated thickness and holes',pcb,'#263537')]
def add(name,x,y,z,w,h,d,color): parts.append((name,box(x,y,z,w,h,d),color))
def photo(name,x,y,w,h,height,color):
 # Dimensioned top-view image: board pixels x=60..701, y=93..584.
 add(name,(x-60)*W/641,(584-y-h)*H/491,T,w*W/641,h*H/491,height,color)
gray='#b2bac1';black='#35383e';green='#73ae78';gold='#c8a84e'
photo('SoM proxy',310,188,181,192,2.2,green)
photo('SoM shield proxy',319,198,164,172,4.3,gray)
photo('Short expansion header proxy',216,118,120,27,8.5,black)
photo('Long expansion header proxy',348,118,296,27,8.5,black)
for start,count in [(36,10),(65,24)]:
 for i in range(count):
  for y in (95.8,98.34): add('Header pin',start+i*2.54,y,T+8.5,.55,.55,2.5,gold)
photo('mini PCIe socket proxy',69,181,145,40,5,black)
photo('RJ45 ETH2 proxy',217,482,79,105,16,gray)
photo('RJ45 ETH1 proxy',313,482,79,105,16,gray)
photo('Dual USB host proxy',412,504,64,83,15.5,gray)
photo('Audio proxy',497,522,46,64,11,black)
photo('USB-C proxy',560,550,43,37,3.2,gray)
photo('DC jack proxy',151,526,48,61,11,black)
photo('Power switch proxy',105,519,31,58,8,black)
photo('Field terminal block proxy',658,177,45,225,12,green)
photo('SMA base proxy',170,101,30,40,7,gold)
photo('SMA projection proxy',171,58,28,43,6,gold)
for y in (446,482): photo('Pushbutton proxy',75,y,33,29,4,gray)
# Small connectors and tall discretes visible in the photos, approximate.
photo('Auxiliary header proxy',675,416,21,50,6,black)
photo('Debug header proxy',679,477,20,48,6,black)
photo('Status header proxy',544,321,48,40,6,black)
for x,y in [(249,415),(346,415),(483,400),(549,399),(616,323)]:
 photo('IC envelope',x,y,29,29,2.0,black)
for y in (169,224,279,334): photo('Power component',244,y,24,27,4,gray)
for x in (98,132): photo('Capacitor proxy',x,133,27,30,7,gray)
# Bottom photo is mirrored into the same board XY coordinates.
add('Bottom LCD FFC proxy',77,97,-2.5,29,5,2.5,gray)
add('Bottom camera FFC proxy',39,97,-2.5,20,5,2.5,gray)
add('Bottom SIM socket proxy',0,59,-2.0,17,16,2.0,gray)
add('Bottom microSD socket proxy',0,40,-1.8,15,15,1.8,gray)
writer=STEPControl_Writer()
for name,solid,color in parts:
 assert BRepCheck_Analyzer(solid).IsValid(),name
 assert writer.Transfer(solid,STEPControl_AsIs)==IFSelect_RetDone
step=OUT/'MAINCTRL_MYD-YF13X_Provisional_Placement_R1.step'
assert writer.Write(str(step))==IFSelect_RetDone
reader=STEPControl_Reader();assert reader.ReadFile(str(step))==IFSelect_RetDone
reader.TransferRoots();shape=reader.OneShape();assert BRepCheck_Analyzer(shape).IsValid()
bb=Bnd_Box();BRepBndLib.AddOptimal_s(shape,bb);v=bb.Get();dims=[v[i+3]-v[i] for i in range(3)]
pb=Bnd_Box();BRepBndLib.AddOptimal_s(pcb,pb);b=pb.Get()
assert abs(b[3]-b[0]-W)<1e-6 and abs(b[4]-b[1]-H)<1e-6
'''
render=old[old.index('def project(p):'):]
render=render.replace('p.X()-87.5,p.Y()-45','p.X()-68.645,p.Y()-52.5').replace('*3.3','*4.0')
render=render.replace('IOCTRL_Provisional_Placement_R1','MAINCTRL_MYD-YF13X_Provisional_Placement_R1')
render=render.replace('IOCTRL — Provisional placement model R1','MYIR MYD-YF13X — Provisional placement model R1').replace('IOCTRL - Provisional placement model R1','MYIR MYD-YF13X - Provisional placement model R1')
render=render.replace('175 × 90 × 40 mm · Based on supplied PoE enclosure image','PCB outline 137.29 x 105 mm | Approximate component geometry')
render=render.replace('175 x 90 x 40 mm | Based on supplied PoE enclosure image','PCB outline 137.29 x 105 mm | Approximate component geometry')
render=render.replace('Estimated mounting slots and connectors. DIN clip and antenna omitted.','PCB thickness, holes and connector heights are estimates. Both sides modelled.')
render=render.replace('Placement reference only. Non-PoE compatibility requires verification. Not for fabrication.','Placement reference only. Verify mounting and cable clearances on actual hardware.')
render=render.replace('Placement reference only. Verify non-PoE compatibility. Not for fabrication.','Placement reference only. Verify mounting and cable clearances on actual hardware.')
render=render.replace("'exported_parts':len(parts)","'exported_parts':len(parts),'pcb_outline_mm':[W,H],'assumed_thickness_mm':T,'assumed_mounting_centres_mm':holes,'assumed_hole_diameter_mm':3.2")
dest=root/'MAINCTRL_MYIR_MYD-YF13X'
(dest/'build_ocp_R1.py').write_text(imports+body+render,encoding='utf-8')

