import fs from 'node:fs/promises';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
import vm from 'node:vm';
import sharp from 'sharp';
const root='C:/Projects/Github/Adherent';
const p=await PresentationFile.importPptx(await FileBlob.load(root+'/SYS/APDU_Design_Review_Questions.pptx'));
const records=(await fs.readFile(root+'/.work/r24/inspect.txt','utf8')).trim().split('\n').map(JSON.parse);
function set(slide,name,text,color){const r=records.find(r=>r.kind==='textbox'&&r.slide===slide&&r.name===name);if(!r)throw Error(name);const s=p.resolve(r.id);s.text=text;if(color)s.text.style={color,bold:true};return s;}
for(const r of records.filter(r=>r.kind==='textbox')){
 let t=r.text.replace(/\bR23\b/g,'R24').replaceAll('APDU_Electrical_Tables_R24.xlsx','APDU_Electrical_Tables_R23.xlsx').replaceAll('11 September 2026','14 September 2026').replaceAll('11 Sep 2026','14 Sep 2026');
 if(t!==r.text)p.resolve(r.id).text=t;
}
set(2,'Text 13','UPS / battery: not approved','#BE3A2B');
set(2,'Text 21','Cellular: not approved','#BE3A2B');
const heading=records.find(r=>r.slide===2&&r.text==='Ten topics, one decision each');p.resolve(heading.id).text='Review topics and meeting decisions';
set(6,'Text 3','Rejected alternatives, retained only as a meeting record.','#BE3A2B');
set(6,'Text 4','The customer rejected UPS and battery backup during the meeting.\nThe customer considers backup power unnecessary.\nThe system uses the existing AC-fed power supplies.');
set(6,'Text 7','MEETING DECISION','#BE3A2B');
const u=set(6,'Text 8','Not approved during the meeting.\nUPS and battery backup are not required.\nExcluded from the electrical design.','#BE3A2B');u.text.style={fontSize:26,color:'#BE3A2B',bold:true};
set(6,'Text 9','Closed: no UPS or backup battery in the R24 drawing.');
set(8,'Text 2','Cellular (LTE) modem');
set(8,'Text 3','MYIR MYD-YF13X MAINCTRL board. Cellular hardware will not be fitted.');
set(8,'Text 4','The customer rejected cellular connectivity during the meeting.\nThe site network carries the vend API and remote service.\nNo cellular modem, SIM, data plan or LTE antennas are included.');
set(8,'Text 7','MEETING DECISION','#BE3A2B');
const c=set(8,'Text 8','Not approved during the meeting.\nCellular connectivity is not required.\nExcluded from the electrical design.','#BE3A2B');c.text.style={fontSize:26,color:'#BE3A2B',bold:true};
set(8,'Text 9','Closed: no cellular connection in the R24 drawing.');
set(14,'Text 1','Meeting decisions and remaining questions');
set(14,'Text 10','Not approved in the meeting. Not required.','#FF7777');
set(14,'Text 16','Not approved in the meeting. Not required.','#FF7777');
set(14,'Text 32','R24 removes cellular and backup power. The remaining questions stay open for the team.');
const img=p.resolve('im/y1g7214f');const frame=img.frame,crop=img.crop,fit=img.fit;
img.replace({blob:new Uint8Array(await fs.readFile(root+'/SYS/Electrical_System_Level_Wiring_Diagram_R24.png')),contentType:'image/png',alt:'Electrical System Level Wiring Diagram R24',fit});img.frame=frame;img.crop=crop;
// Update the existing vector diagram sources without redesigning the slides.
const src=await fs.readFile('C:/Users/umtky/AppData/Local/Temp/claude/C--Projects-Github-Adherent/4efd77b9-e57d-41f1-a4b3-59a544cf628a/scratchpad/build_deck.js','utf8');
const illustrations=vm.runInNewContext(src.slice(src.indexOf('const S ='),src.indexOf('(async () =>'))+';ILL;');
for(const [id,svg] of [['im/8rqxsni1',illustrations.eth.replace('Wi-Fi / BT · LTE antennas','Wi-Fi / BT antennas')],['im/vitwz65k',illustrations.cam.replace('not in R23','not in R24')]]){
 const im=p.resolve(id),f=im.frame,cr=im.crop,ft=im.fit;
 im.replace({blob:new Uint8Array(await sharp(Buffer.from(svg)).png().toBuffer()),contentType:'image/png',fit:ft});im.frame=f;im.crop=cr;
}
await (await PresentationFile.exportPptx(p)).save(root+'/.work/r24/candidate.pptx');
for(let i=0;i<p.slides.items.length;i++){const b=await p.slides.items[i].export({format:'png',scale:1});await fs.writeFile(`${root}/.work/r24/after-${i+1}.png`,new Uint8Array(await b.arrayBuffer()));}
console.log('Exported and rendered 14 slides');


