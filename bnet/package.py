"""Create the clean BNet ESO release from a retained runtime tar snapshot."""
from pathlib import Path,PurePosixPath
import argparse,tarfile,gzip,hashlib,io,json,re,posixpath,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import runtime
ROOT=Path(__file__).resolve().parents[1]
INPUT_ROOT='GE-Proton11-7-ESO-BNet-Compare-arm64'
SECRET=re.compile(rb'-----BEGIN (?:OPENSSH |RSA |DSA |EC |ENCRYPTED )?PRIVATE KEY-----|github_pat_[A-Za-z0-9_]{30,}|gh[pousr]_[A-Za-z0-9]{30,}')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--forbid-home',action='append',default=[]);a=p.parse_args()
 runtime.require(not a.output.exists() and a.input.resolve()!=a.output.resolve(),'New separate output required')
 private=[s.encode() for s in a.forbid_home]+[str(Path.home()).encode()]
 private+=[s.decode().encode('utf-16le') for s in private]
 index={};seen=set();input_hashes={};old_index=None;core={}
 def checked(data,name):
  runtime.require(not SECRET.search(data) and not any(v in data for v in private),'Private data in '+name)
 def entry(tar,name,payload=None,mode=0o644,kind=tarfile.REGTYPE,link=''):
  runtime.require(name not in seen,'Duplicate packaged path: '+name);seen.add(name)
  m=tarfile.TarInfo(runtime.TOOL_ID+'/'+name);m.uid=m.gid=m.mtime=0;m.uname=m.gname='';m.mode=mode;m.type=kind;m.linkname=link
  if payload is None:tar.addfile(m)
  else:
   checked(payload,name);m.size=len(payload);tar.addfile(m,io.BytesIO(payload));index[name]=hashlib.sha256(payload).hexdigest()
 vdf=f'''"compatibilitytools"
{{
 "compat_tools"
 {{
  "{runtime.TOOL_ID}"
  {{
   "install_path" "."
   "display_name" "{runtime.DISPLAY_NAME}"
   "from_oslist" "windows"
   "to_oslist" "linux"
  }}
 }}
}}
'''.encode()
 overrides={'compatibilitytool.vdf':vdf,'version':('1789520806 '+runtime.TOOL_ID+'-v0.4.0\n').encode()}
 with a.output.open('xb') as out,gzip.GzipFile(filename='',fileobj=out,mode='wb',compresslevel=3,mtime=0) as gz,tarfile.open(fileobj=gz,mode='w|') as dest,tarfile.open(a.input,'r|') as source:
  for member in source:
   parts=PurePosixPath(member.name).parts
   runtime.require(parts and parts[0]==INPUT_ROOT and '..' not in parts and not member.name.startswith('/') and '\\' not in member.name,'Unsafe snapshot entry')
   if len(parts)==1:continue
   name=PurePosixPath(*parts[1:]).as_posix()
   if runtime.excluded(name):continue
   if member.isfile():
    runtime.require(member.size<512*1024*1024,'Oversize runtime input')
    data=source.extractfile(member).read()
    if name=='eso-comparison/RUNTIME-SHA256SUMS':old_index=data.decode();continue
    input_hashes[name]=hashlib.sha256(data).hexdigest()
    if name in runtime.COMPONENTS:core[name]=input_hashes[name]
   else:data=None
   if name.startswith('eso-comparison/'):
    if not name.startswith('eso-comparison/LICENSES'):continue
    name='eso-bnet/LICENSES/runtime'+name[len('eso-comparison/LICENSES'):]
   if name=='eso-comparison' or name in overrides:continue
   if member.isdir():entry(dest,name,mode=0o755,kind=tarfile.DIRTYPE)
   elif member.issym():
    target=posixpath.normpath(posixpath.join(posixpath.dirname(name),member.linkname))
    runtime.require(not PurePosixPath(member.linkname).is_absolute() and target!='..' and not target.startswith('../') and '\\' not in member.linkname,'External snapshot symlink')
    entry(dest,name,mode=0o777,kind=tarfile.SYMTYPE,link=member.linkname)
   else:
    runtime.require(member.isfile(),'Special snapshot node');entry(dest,name,data,0o755 if member.mode&0o111 else 0o644)
  runtime.require(core==runtime.COMPONENTS,'Snapshot core hashes mismatch')
  runtime.require(old_index is not None,'Snapshot has no original checksum index')
  original={}
  for line in old_index.splitlines():
   value,name=line.split('  ',1);runtime.require(name not in original,'Duplicate original checksum entry');original[name]=value
  runtime.require(original==input_hashes,'Installed runtime differs from its verified file index')
  for name,data in overrides.items():entry(dest,name,data)
  # Current public sources and docs replace device-era comparison metadata.
  for directory,prefix in [('bnet','eso-bnet'),('docs','eso-bnet/docs')]:
   for path in sorted((ROOT/directory).rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts or path.suffix=='.pyc':continue
    relative=path.relative_to(ROOT/directory).as_posix()
    if directory=='bnet' and relative=='README.md':continue
    entry(dest,prefix+'/'+relative,path.read_bytes())
  entry(dest,'eso-bnet/README.md',(ROOT/'README.md').read_bytes())
  entry(dest,'README-ESO.txt',('Install '+runtime.DISPLAY_NAME+' by extracting this folder into ~/.local/share/Steam/compatibilitytools.d/ and restarting Steam.\nSources and upstream credit: https://github.com/mrdidit/bnet-arm\nSee eso-bnet/docs/INSTALL.md and RUNTIME-SOURCES.txt.\n').encode())
  source_text='BNet1 on GE-Proton11-7 ARM64. Sources accompany release v0.4.0.\nhttps://github.com/dxu16/eso-arm64ec-wine-fix/releases/tag/v0.4.0\nOriginal BNet: https://github.com/mrdidit/bnet-arm\n\n'
  for row in json.loads((ROOT/'bnet/source-manifest.json').read_text())['assets']:source_text+=row['sha256']+'  '+row['name']+'\n'+row['url']+'\n'
  source_text+='ESO-BNet-v0.4.0-patch-sources.tar.gz contains the additional ESO transformations and manifests.\n'
  entry(dest,'RUNTIME-SOURCES.txt',source_text.encode())
  sums=''.join(value+'  '+name+'\n' for name,value in sorted(index.items())).encode()
  # The index intentionally excludes its own digest.
  entry(dest,runtime.INDEX,sums)
 result=runtime.verify(a.output)
 result['archive_bytes']=a.output.stat().st_size
 a.output.with_suffix('.validation.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
