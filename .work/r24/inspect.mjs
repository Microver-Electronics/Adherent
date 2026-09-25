import fs from 'node:fs/promises';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
const p=await PresentationFile.importPptx(await FileBlob.load('C:/Projects/Github/Adherent/SYS/APDU_Design_Review_Questions.pptx'));
await fs.writeFile('C:/Projects/Github/Adherent/.work/r24/inspect.txt',(await p.inspect({kind:'slide,textbox,image',maxChars:1000000})).ndjson);
for(const n of [2,6,8,14]) {const b=await p.slides.items[n-1].export({format:'png',scale:1});await fs.writeFile(`C:/Projects/Github/Adherent/.work/r24/before-${n}.png`,new Uint8Array(await b.arrayBuffer()));}
