"""Verify BNet ESO DLLs, exact reproduction, and rejection guards; no game launch."""
from pathlib import Path
import importlib.util,hashlib,json,struct,sys,tempfile,subprocess
ROOT=Path(__file__).resolve().parent
def check(v,msg):
 if not v:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 spec=importlib.util.spec_from_file_location('bnet_patch',ROOT/'reproduce.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 for component in ['kernel32','ntdll']:
  patched=(ROOT/'bin'/f'{component}.dll').read_bytes();original=bytearray(patched)
  manifest=json.loads((ROOT/('kernel32-hotpatch-thunks.json' if component=='kernel32' else 'ntdll-performance.json')).read_text())
  _,_,offset=m.pe_layout(patched)
  for row in manifest['changes']:
   pos=offset(int(row['rva'],16));old=bytes.fromhex(row['old']);new=bytes.fromhex(row['new'])
   check(original[pos:pos+len(new)]==new,'Patch manifest mismatch')
   original[pos:pos+len(old)]=old
  expected=m.KERNEL_IN if component=='kernel32' else m.LAYOUTS['bnet']['sha']
  check(sha(original)==expected,'Original baseline reconstruction mismatch')
  new,_=m.kernel(original) if component=='kernel32' else m.ntdll(original,'bnet')
  check(new==patched,'Reproduction mismatch')
  if component=='ntdll':
   helper=patched[0xf1210:0xf1238]
   check(helper.hex()=='110100581f0211eb80000054313dec58bf61ff171f2003d56b210091d861ff17488da42400000000','Independent assembler reference mismatch')
  with tempfile.TemporaryDirectory(prefix='eso-bnet-',dir=ROOT) as t:
   t=Path(t);source=t/'original.dll';out=t/'output.dll';bad=t/'bad.dll'
   source.write_bytes(original);bad.write_bytes(b'unsupported')
   subprocess.run([sys.executable,'-B',str(ROOT/'reproduce.py'),'bnet',component,str(source),str(out)],check=True)
   check(out.read_bytes()==patched,'CLI reproduction mismatch')
   for a,b in [(source,source),(source,out),(bad,t/'rejected.dll')]:
    r=subprocess.run([sys.executable,'-B','-O',str(ROOT/'reproduce.py'),'bnet',component,str(a),str(b)],capture_output=True)
    check(r.returncode!=0,'Unsafe input accepted')
   check(not (t/'rejected.dll').exists(),'Rejected input wrote a DLL')
 print('PASS: BNet ESO kernel32 and ntdll hashes, exact reproduction, helper bytes and rejection guards')
if __name__=='__main__':main()
