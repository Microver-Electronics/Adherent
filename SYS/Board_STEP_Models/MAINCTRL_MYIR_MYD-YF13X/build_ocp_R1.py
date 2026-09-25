"""Provisional placement model, mm. Requires cadquery-ocp. Read MODEL_NOTES_R1.md."""
from pathlib import Path
import json
from OCP.gp import gp_Pnt, gp_Trsf, gp_Vec
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer, STEPControl_Reader, STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location

OUT=Path(__file__).resolve().parent
def box(x,y,z,dx,dy,dz): return BRepPrimAPI_MakeBox(gp_Pnt(x,y,z),dx,dy,dz).Shape()
def cylinder(x,y,r,h):
 tr=gp_Trsf();tr.SetTranslation(gp_Vec(x,y,0))
 return BRepBuilderAPI_Transform(BRepPrimAPI_MakeCylinder(r,h).Shape(),tr,True).Shape()
def cut(a,b): return BRepAlgoAPI_Cut(a,b).Shape()
W,H,T=137.29,105.0,1.6
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
def project(p):
 x,y,z=p.X()-68.645,p.Y()-52.5,p.Z()
 return (550+(x*.866+y*.5)*4.0,410+(x*.29-y*.5-z*.816)*4.0,x*.408-y*.707+z*.577)
triangles=[]
for name,solid,color in parts:
 BRepMesh_IncrementalMesh(solid,.25);exp=TopExp_Explorer(solid,TopAbs_FACE)
 while exp.More():
  face=TopoDS.Face_s(exp.Current());loc=TopLoc_Location();tri=BRep_Tool.Triangulation_s(face,loc)
  if tri:
   for i in range(1,tri.NbTriangles()+1):
    pts=[project(tri.Node(j).Transformed(loc.Transformation())) for j in tri.Triangle(i).Get()]
    triangles.append((sum(p[2] for p in pts)/3,color,pts))
  exp.Next()
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="650"><rect width="1100" height="650" fill="white"/>',
 '<text x="36" y="44" font-family="Arial" font-size="24" fill="#203141">DOORIO â€” Provisional placement model R1</text>',
 '<text x="36" y="75" font-family="Arial" font-size="16" fill="#52616d">175 Ã— 90 Ã— 40 mm Â· Based on supplied PoE enclosure image</text>']
for depth,color,pts in sorted(triangles,key=lambda t:t[0]):
 svg.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y,z in pts)+f'" fill="{color}" stroke="{color}" stroke-width="0.3"/>')
svg+=['<text x="36" y="592" font-family="Arial" font-size="16" fill="#a44621">PCB thickness, holes and connector heights are estimates. Both sides modelled.</text>',
 '<text x="36" y="622" font-family="Arial" font-size="16" fill="#52616d">Placement reference only. Verify mounting and cable clearances on actual hardware.</text></svg>']
(OUT/'MAINCTRL_MYD-YF13X_Provisional_Placement_R1.svg').write_text('\n'.join(svg),encoding='utf-8')
import numpy as np
from PIL import Image,ImageDraw,ImageFont
pixels=np.full((650,1100,3),255,dtype=np.uint8);depthbuf=np.full((650,1100),-np.inf)
for _,color,pts in triangles:
 (x0,y0,z0),(x1,y1,z1),(x2,y2,z2)=pts
 den=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
 if abs(den)<1e-8: continue
 lx=max(0,int(min(x0,x1,x2)));rx=min(1099,int(max(x0,x1,x2))+1)
 ly=max(0,int(min(y0,y1,y2)));ry=min(649,int(max(y0,y1,y2))+1)
 yy,xx=np.mgrid[ly:ry+1,lx:rx+1];xx=xx+.5;yy=yy+.5
 a=((y1-y2)*(xx-x2)+(x2-x1)*(yy-y2))/den
 b=((y2-y0)*(xx-x2)+(x0-x2)*(yy-y2))/den;c=1-a-b
 zz=a*z0+b*z1+c*z2
 mask=(a>=-1e-8)&(b>=-1e-8)&(c>=-1e-8)&(zz>depthbuf[ly:ry+1,lx:rx+1])
 depthbuf[ly:ry+1,lx:rx+1][mask]=zz[mask]
 pixels[ly:ry+1,lx:rx+1][mask]=[int(color[i:i+2],16) for i in (1,3,5)]
im=Image.fromarray(pixels);d=ImageDraw.Draw(im)
font=lambda sz:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',sz)
d.text((36,24),'MYIR MYD-YF13X - Provisional placement model R1',font=font(24),fill='#203141')
d.text((36,60),'PCB outline 137.29 x 105 mm | Approximate component geometry',font=font(16),fill='#52616d')
d.text((36,575),'PCB thickness, holes and connector heights are estimates. Both sides modelled.',font=font(16),fill='#a44621')
d.text((36,605),'Placement reference only. Verify mounting and cable clearances on actual hardware.',font=font(16),fill='#52616d')
im.save(OUT/'MAINCTRL_MYD-YF13X_Provisional_Placement_R1.png')
(OUT/'validation_R1.json').write_text(json.dumps({'units':'mm','reimport_valid':True,'bounding_box_mm':dims,'exported_parts':len(parts),'pcb_outline_mm':[W,H],'assumed_thickness_mm':T,'assumed_mounting_centres_mm':holes,'assumed_hole_diameter_mm':3.2,'status':'Provisional; see MODEL_NOTES_R1.md'},indent=2))
print(json.dumps({'file':str(step),'dimensions_mm':dims,'valid':True}))
