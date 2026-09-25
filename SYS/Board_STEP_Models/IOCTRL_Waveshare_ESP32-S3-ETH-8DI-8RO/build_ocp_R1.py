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
base=box(0,0,0,175,90,10)
for x in (5,170):
 for y in (10,80):
  slot=BRepAlgoAPI_Fuse(cylinder(x,y-.75,2.25,10),cylinder(x,y+.75,2.25,10)).Shape()
  slot=BRepAlgoAPI_Fuse(slot,box(x-2.25,y-.75,0,4.5,1.5,10)).Shape()
  base=cut(base,slot)
housing=box(10,0,10,155,90,30)
housing=cut(cut(housing,box(25,-1,15,125,14,26)),box(25,77,15,125,14,26))
housing=cut(housing,box(20,14,38.5,135,62,2))
parts=[('Base',base,'#383d42'),('Housing',housing,'#25292d'),('Cover',box(20,14,38.5,135,62,1.5),'#43494f'),
 ('Relay terminals',box(25,1,10,125,11,14),'#72a86f'),('RS485',box(25,78,15,16,11,10),'#72a86f'),
 ('Power',box(43,78,15,11,11,10),'#72a86f'),('DI',box(56,78,15,52,11,10),'#72a86f'),
 ('USB',box(114,79,15,9,9,5),'#bdc2c6'),('Ethernet',box(127,76,15,16,14,14),'#bdc2c6')]
writer=STEPControl_Writer()
for name,shape,color in parts:
 assert BRepCheck_Analyzer(shape).IsValid(),name
 assert writer.Transfer(shape,STEPControl_AsIs)==IFSelect_RetDone
step=OUT/'IOCTRL_Provisional_Placement_R1.step'
assert writer.Write(str(step))==IFSelect_RetDone
reader=STEPControl_Reader();assert reader.ReadFile(str(step))==IFSelect_RetDone
reader.TransferRoots();shape=reader.OneShape();assert BRepCheck_Analyzer(shape).IsValid()
bb=Bnd_Box();BRepBndLib.AddOptimal_s(shape,bb);v=bb.Get();dims=[v[i+3]-v[i] for i in range(3)]
assert all(abs(a-b)<1e-5 for a,b in zip(dims,[175,90,40])),dims
def project(p):
 x,y,z=p.X()-87.5,p.Y()-45,p.Z()
 return (550+(x*.866+y*.5)*3.3,410+(x*.29-y*.5-z*.816)*3.3,x*.408-y*.707+z*.577)
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
 '<text x="36" y="44" font-family="Arial" font-size="24" fill="#203141">IOCTRL — Provisional placement model R1</text>',
 '<text x="36" y="75" font-family="Arial" font-size="16" fill="#52616d">175 × 90 × 40 mm · Based on supplied PoE enclosure image</text>']
for depth,color,pts in sorted(triangles,key=lambda t:t[0]):
 svg.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y,z in pts)+f'" fill="{color}" stroke="{color}" stroke-width="0.3"/>')
svg+=['<text x="36" y="592" font-family="Arial" font-size="16" fill="#a44621">Estimated mounting slots and connectors. DIN clip and antenna omitted.</text>',
 '<text x="36" y="622" font-family="Arial" font-size="16" fill="#52616d">Placement reference only. Non-PoE compatibility requires verification. Not for fabrication.</text></svg>']
(OUT/'IOCTRL_Provisional_Placement_R1.svg').write_text('\n'.join(svg),encoding='utf-8')
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
d.text((36,24),'IOCTRL - Provisional placement model R1',font=font(24),fill='#203141')
d.text((36,60),'175 x 90 x 40 mm | Based on supplied PoE enclosure image',font=font(16),fill='#52616d')
d.text((36,575),'Estimated mounting slots and connectors. DIN clip and antenna omitted.',font=font(16),fill='#a44621')
d.text((36,605),'Placement reference only. Verify non-PoE compatibility. Not for fabrication.',font=font(16),fill='#52616d')
im.save(OUT/'IOCTRL_Provisional_Placement_R1.png')
(OUT/'validation_R1.json').write_text(json.dumps({'units':'mm','reimport_valid':True,'bounding_box_mm':dims,'exported_parts':len(parts),'status':'Provisional; see MODEL_NOTES_R1.md'},indent=2))
print(json.dumps({'file':str(step),'dimensions_mm':dims,'valid':True}))
