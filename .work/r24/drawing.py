from pathlib import Path
import xml.etree.ElementTree as ET
import re
p=Path('C:/Projects/Github/Adherent/SYS')
t=ET.parse(p/'Electrical_System_Level_Wiring_Diagram_R23.drawio')
for c in t.iter('mxCell'):
 v=c.get('value','')
 if c.get('id')=='sbc':
  v=v.replace(' · mini-PCIe (USB) + SIM (LTE option)','')
 if c.get('id')=='title': v=v.replace('R23','R24').replace('2026-09-11','2026-09-14')
 c.set('value',v) if 'value' in c.attrib else None
out=p/'Electrical_System_Level_Wiring_Diagram_R24.drawio'
t.write(out,encoding='utf-8',xml_declaration=True)
assert not re.search(r'\b(cellular|ups|battery|batteries|lte|gsm|sim|mini-pcie)\b',out.read_text('utf-8'),re.I)
ids={c.get('id') for c in t.iter('mxCell')}
assert all(c.get(k) in ids for c in t.iter('mxCell') for k in ('source','target') if c.get(k))
print(out)
