"""Exercise archive integrity and symlink guards with small standalone fixtures."""
from pathlib import Path
import tarfile,tempfile,io,hashlib,sys
import runtime
def main():
 old=runtime.COMPONENTS
 runtime.COMPONENTS={'proton':hashlib.sha256(b'launcher').hexdigest()}
 base={'proton':b'launcher','compatibilitytool.vdf':b'metadata','toolmanifest.vdf':b'manifest','version':b'version','eso-bnet/source-manifest.json':b'{}','RUNTIME-SOURCES.txt':b'sources','real/file':b'data'}
 def fixture(path,kind):
  entries=dict(base)
  index=''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n' for name,data in entries.items()).encode()
  if kind=='tamper':entries['real/file']=b'tampered'
  with tarfile.open(path,'w:gz') as t:
   for name,data in entries.items():
    m=tarfile.TarInfo(runtime.TOOL_ID+'/'+name);m.size=len(data)
    if kind=='owner':m.uid=1
    t.addfile(m,io.BytesIO(data))
   if kind!='no-index':
    m=tarfile.TarInfo(runtime.TOOL_ID+'/'+runtime.INDEX);m.size=len(index);t.addfile(m,io.BytesIO(index))
   if kind=='traversal':t.addfile(tarfile.TarInfo('../escape'))
   if kind=='duplicate':t.addfile(tarfile.TarInfo(runtime.TOOL_ID+'/proton'))
   if kind in {'alias','external','chain-escape'}:
    links={'alias':'real','alias-file':'alias/file'} if kind=='alias' else {'bad':'../../outside'} if kind=='external' else {'a':'.','bad':'a/../outside'}
    # Include a real directory so alias chains resolve exactly as on disk.
    directory=tarfile.TarInfo(runtime.TOOL_ID+'/real');directory.type=tarfile.DIRTYPE;t.addfile(directory)
    for name,target in links.items():
     m=tarfile.TarInfo(runtime.TOOL_ID+'/'+name);m.type=tarfile.SYMTYPE;m.linkname=target;t.addfile(m)
 try:
  with tempfile.TemporaryDirectory(prefix='eso-bnet-archive-',dir=Path(__file__).resolve().parent) as tmp:
   if Path(tmp).resolve().parent!=Path(__file__).resolve().parent:raise ValueError('Unexpected temporary path')
   root=Path(tmp)
   for kind in ['valid','alias','traversal','duplicate','owner','no-index','tamper','external','chain-escape']:
    path=root/(kind+'.tar.gz');fixture(path,kind)
    try:runtime.verify(path)
    except ValueError:
     if kind in {'valid','alias'}:raise
    else:
     if kind not in {'valid','alias'}:raise AssertionError('Unsafe fixture accepted: '+kind)
 finally:runtime.COMPONENTS=old
 print('PASS: valid archive/alias chain; traversal, duplicates, ownership, missing index, tampering and escaping links rejected')
if __name__=='__main__':main()
