from pathlib import Path
import xml.etree.ElementTree as ET
import re,copy
p=Path('C:/Projects/Github/Adherent/SYS')
t=ET.parse(p/'Electrical_System_Level_Wiring_Diagram_R24.drawio');root=t.find('.//root')
c={e.get('id'):e for e in root.findall('mxCell')}
def val(i,s):c[i].set('value',s)
def geo(i,**kw):
 for k,v in kw.items():c[i].find('mxGeometry').set(k,str(v))
def sty(i,**kw):
 s=c[i].get('style','')
 for k,v in kw.items():
  s=re.sub(r'(?<!\w)'+k+r'=[^;]*;', '',s)+f'{k}={v};'
 c[i].set('style',s)
def route(i,pts,lab=0):
 g=c[i].find('mxGeometry')
 for child in list(g):g.remove(child)
 g.set('x',str(lab))
 if pts:
  a=ET.SubElement(g,'Array',{'as':'points'})
  for x,y in pts:ET.SubElement(a,'mxPoint',{'x':str(x),'y':str(y)})
for i in ['psu48','e_ac12','e_ac48','e_48dist']:root.remove(c[i])
c['psu12'].set('id','dcdc12');c['dcdc12']=c.pop('psu12')
val('title',c['title'].get('value').replace('R24','R25').replace('2026-09-14','2026-09-24'))
val('g_power','AC INPUT &amp; SINGLE 24 V POWER SUPPLY')
val('psu24','<b>PSU1 · 24 V · Mean Well RSP-500-24</b><br>Only AC/DC PSU · nominal 500 W<br>Combined load / concurrency budget to be recalculated')
geo('psu24',width=460,height=100)
val('dcdc12','<b>24 V → 12 V conversion · REQUIRED / TBC</b><br>DC/DC implementation, MPN and current rating not selected<br>Maintains existing 12 V loads; powered from PSU1')
geo('dcdc12',x=70,y=940,width=460,height=85)
sty('dcdc12',strokeColor='#9A6510',dashed=1)
val('pwr_note','Single 24 V AC/DC source. Derived 12 V shown provisionally for MYIR, existing custom-board logic and 12 V latches. No change to custom PCB count.')
geo('pwr_note',y=1040,height=55)
sty('e_ac24',exitX=.5);route('e_ac24',[])
sty('e_24dist',exitX=1,exitY=.5);val('e_24dist','W03 · 24 V');route('e_24dist',[(600,820),(600,720)],.5)
c['e_12dist'].set('source','dcdc12');sty('e_12dist',exitX=1,exitY=.5);val('e_12dist','W04 · derived 12 V');route('e_12dist',[(640,982.5),(640,750)],.55)
new=copy.deepcopy(c['e_24dist']);new.set('id','e_buck_in');new.set('source','psu24');new.set('target','dcdc12');root.append(new);c['e_buck_in']=new
val('e_buck_in','24 V · fused branch, rating TBC');sty('e_buck_in',exitX=.5,exitY=1,entryX=.5,entryY=0);route('e_buck_in',[])
val('dist','<b>24 V + derived 12 V · separate fused rails / common 0 V</b><br>24 V: F1–F10 lane motors · F11 chuck · F15/F16 gantry (TBC) · F17 IOCTRL<br>Derived 12 V: F12 SYSCTRL · F13 MAINCTRL · F14 lane logic · F18 latch contacts<br>Fuse ratings and cable sizes require review for the single-PSU architecture')
val('motion',c['motion'].get('value').replace('(drivers integrated in the motors)','(driver packaging and interface TBC)').replace('24 V brake out','brake out (voltage TBC)'))
for i in ['xstep','zstep']:
 s=c[i].get('value').replace(' + integrated drive',' + supplied driver').replace('24–48 V in','Proposed 24 V input: supplier confirmation required')
 val(i,s)
for i in ['e_48x','e_48z']:
 val(i,c[i].get('value').replace('48 V','24 V (TBC)'));sty(i,dashed=1)
val('ioctrl','<b>IOCTRL · Waveshare ESP32-S3-ETH-8DI-8RO · COTS ×1</b><br><b>Module power: 24 V via F17 / W34</b> · rated input 7–36 V<br>MAINCTRL ↔ isolated RS485 · planned Modbus RTU firmware<br><b>Relay COM supply: separate derived 12 V via F18 / W35</b><br>RO1–4: latches · DI1–5: door sensors · RO5–8: reserved · Wi-Fi / BLE / Ethernet unused')
geo('ioctrl',height=120);sty('ioctrl',fillColor='#EEF3F9',strokeColor='#1D5FA8',fontSize=12)
geo('g_doors',height=400);geo('latches',y=1080,height=85);geo('doorsens',y=1080,height=85);geo('dooract',y=1190,height=40)
sty('e_rs485',entryY=.30)
val('e_12ioctrl','W34 · F17 · 24 V module');sty('e_12ioctrl',entryY=.525)
new=copy.deepcopy(c['e_12ioctrl']);new.set('id','e_contact12');root.append(new);c['e_contact12']=new
val('e_contact12','W35 · F18 · 12 V relay COM');sty('e_contact12',exitY=.8,entryY=.83333);route('e_contact12',[(1600,786),(1600,1000)],.8)
val('e_latch','Switched 12 V · RO1–4');route('e_latch',[])
val('e_doorsens','DI1–5');route('e_doorsens',[])
route('e_dooract',[(1700,1045),(1655,1045),(1655,1210)])
val('legend','<font color="#BE3A2B"><b>━━</b></font> DC power (bold): 24 V / derived 12 V &nbsp; ━━ AC / motor phases &nbsp; <font color="#1D5FA8">━━</font> data / control &nbsp; ┄┄ unconfirmed / wireless')
val('tables_ref','<b>R25 diagram update:</b> one 24 V PSU; IOCTRL powered at 24 V; separate 12 V relay-contact feed. <b>R23 Excel is historical:</b> PSU, fuse, cable and power entries are not yet aligned. W35 / F18 are provisional new references; W02 / W31 / W32 retired.')
geo('tables_ref',height=55)
out=p/'Electrical_System_Level_Wiring_Diagram_R25.drawio';t.write(out,encoding='utf-8',xml_declaration=True)
ids={e.get('id') for e in root.findall('mxCell')}
assert len(ids)==len(root.findall('mxCell'))
assert all(e.get(k) in ids for e in root.findall('mxCell') for k in ('source','target') if e.get(k))
assert not any(s in out.read_text('utf-8') for s in ['48 V','PSU2','PSU3','LRS-150','S-500-48'])
print(out)
