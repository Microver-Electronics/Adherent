from pathlib import Path
import xml.etree.ElementTree as ET
import re
p=Path('C:/Projects/Github/Adherent/SYS')
t=ET.parse(p/'Electrical_System_Level_Wiring_Diagram_R25.drawio');root=t.find('.//root');c={e.get('id'):e for e in root.findall('mxCell')}
def val(i,s):c[i].set('value',s)
def sty(i,**kw):
 s=c[i].get('style','')
 for k,v in kw.items():s=re.sub(r'(?<!\w)'+k+r'=[^;]*;','',s)+f'{k}={v};'
 c[i].set('style',s)
def route(i,pts=(),x=0):
 g=c[i].find('mxGeometry')
 for a in list(g):g.remove(a)
 g.set('x',str(x))
 if pts:
  a=ET.SubElement(g,'Array',{'as':'points'})
  for px,py in pts:ET.SubElement(a,'mxPoint',{'x':str(px),'y':str(py)})
root.remove(c['e_buck_in'])
val('title',c['title'].get('value').replace('R25','R26'))
val('motion','<b>SYSCTRL · custom STM32 machine controller ×1</b><br>HW_ADHERENT_SYSCTRL_R1 · FW_ADHERENT_SYSCTRL_R1<br><b>Gantry:</b> STEP / DIR / ENA, ALARM, brake control (interface TBC)<br>Basket servo: PWM + local 6.8 V buck · 6 × opto inputs<br><b>Labeling:</b> chuck rotate + jaw stepper drivers · jaw home input<br>CAN node · stack light / auxiliary I/O · IOCTRL handles doors<br><b>24 V inputs:</b> F11 motor rail (W06), F12 converter supply (W07)')
sty('motion',verticalAlign='top',spacingTop=8)
val('dcdc12','<b>ON SYSCTRL: 24 V → 12 V buck converter</b><br>Feeds local logic / servo buck, MAINCTRL, lane logic and latch contacts<br>On-board F14 branch → lane bus · converter MPN / current rating TBC')
c['dcdc12'].set('id','sysctrl_buck');c['sysctrl_buck']=c.pop('dcdc12')
g=c['sysctrl_buck'].find('mxGeometry');g.attrib.update(x='810',y='550',width='460',height='60')
sty('sysctrl_buck',strokeColor='#BE3A2B',dashed=0,fillColor='#FFF4EE',fontSize=11)
# Place this internal block after its SYSCTRL parent in drawing order.
root.remove(c['sysctrl_buck']);root.insert(list(root).index(c['motion'])+1,c['sysctrl_buck'])
val('pwr_note','Only PSU1 supplies the system at 24 V. The 24 V → 12 V buck converter is integrated on SYSCTRL. No separate DC/DC module. Converter rating must cover all connected 12 V loads.')
g=c['pwr_note'].find('mxGeometry');g.set('y','925');g.set('height','100')
val('dist','<b>DIN distribution · 24 V rail + separate SYSCTRL-derived 12 V rail</b><br>24 V: F1–F10 lanes · F11 SYSCTRL motors · F12 SYSCTRL buck · F15/F16 gantry (TBC) · F17 IOCTRL<br>12 V from SYSCTRL W04: F13 MAINCTRL · F18 latch contacts<br>F14 lane-logic protection is on SYSCTRL. All ratings / wire sizes require review.')
val('e_12sys','W07 · F12 · 24 V buck input');sty('e_12sys',exitX=.5,entryX=.5)
val('e_12dist','W04 · 12 V OUT');c['e_12dist'].set('source','motion');sty('e_12dist',exitX=.85,exitY=1,entryX=.85,entryY=0);route('e_12dist')
val('e_rs1',c['e_rs1'].get('value').replace('CAN + 12 V bus cable','CAN + SYSCTRL 12 V (F14)'))
val('ioctrl',c['ioctrl'].get('value').replace('separate derived 12 V via F18 / W35','SYSCTRL-derived 12 V via F18 / W35'))
val('tables_ref','<b>R26:</b> single 24 V PSU; 24→12 V conversion on SYSCTRL; W07 = 24 V input, W04 = SYSCTRL 12 V output. F14 lane branch is on SYSCTRL. <b>R23 Excel is historical and not aligned:</b> power, fuse and cable entries need revision. W35/F18 provisional; W02/W31/W32 retired.')
out=p/'Electrical_System_Level_Wiring_Diagram_R26.drawio';t.write(out,encoding='utf-8',xml_declaration=True)
ids={e.get('id') for e in root.findall('mxCell')}
assert all(e.get(k) in ids for e in root.findall('mxCell') for k in ('source','target') if e.get(k))
assert c['e_12dist'].get('source')=='motion'
assert '12 V logic rail (F12) in' not in out.read_text('utf-8')
print(out)
