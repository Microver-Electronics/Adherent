import {finalizePresentation} from 'file:///C:/Users/umtky/.codex/plugins/cache/openai-primary-runtime/presentations/26.905.11957/skills/presentations/container_tools/artifact_tool_utils.mjs';
const root='C:/Projects/Github/Adherent';
const skill='C:/Users/umtky/.codex/plugins/cache/openai-primary-runtime/presentations/26.905.11957/skills/presentations';
const result=await finalizePresentation({workspaceDir:root,candidatePath:root+'/.work/r24/candidate.pptx',finalPath:root+'/SYS/APDU_Design_Review_Questions_R24.pptx',pythonExecutable:'C:/Users/umtky/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],explicitTotalSlideCount:14,verifyArtifactToolImport:true,receiptPath:root+'/.work/r24/validation-final.json'});
console.log(JSON.stringify(result));


