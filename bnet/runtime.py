"""Verify the self-contained BNet-based ESO runtime archive, without executing it."""
from pathlib import Path,PurePosixPath
import hashlib,json,tarfile,posixpath,sys
TOOL_ID='GE-Proton11-7-ESO-BNet-arm64'
DISPLAY_NAME='GE-Proton11-7 ESO BNet (ARM64, experimental)'
COMPONENTS={
 'files/lib/wine/aarch64-windows/kernel32.dll':'5b9c2d116f93a307e7b69c31544e52b7a5081fa7caa384020b1c09f948664d5b',
 'files/lib/wine/aarch64-windows/ntdll.dll':'5da92139e0e34111acf952b4d7ba590da09d34fdb9e99b68086c6081bcda16ac',
 'files/lib/wine/aarch64-windows/libarm64ecfex.dll':'27e2b27b7c11e847ac4687614ebcedc02854938427b43eefb5e64b099bad2733',
 'files/lib/wine/aarch64-windows/libwow64fex.dll':'6ea8765fdc9436e44020fba1af2b389bafaab0cbd542939ca43f0cc4171b8d51',
 'files/lib/wine/aarch64-unix/libarm64ecfex.so':'fa41dfc7857d6cfe3cc07e3aa948ee710a3a771b59c2deaab81931298e287b11',
 'files/lib/wine/aarch64-unix/libwow64fex.so':'df8e7e0da785421714faf9d7b75346536643afc768ac905f457c33b9ebfde216',
}
INDEX='eso-bnet/RUNTIME-SHA256SUMS'
def require(value,message):
 if not value:raise ValueError(message)
def excluded(name):
 p=PurePosixPath(name)
 return any(x.startswith('default_pfx') for x in p.parts) or any(x in {'.git','__pycache__','pfx','compatdata'} for x in p.parts) or p.name in {'dist.lock','user_settings.py','steampipe_fixups_mtime'} or p.suffix in {'.pyc','.pyo'}
def safe_name(name):
 p=PurePosixPath(name)
 require(not p.is_absolute() and '..' not in p.parts and '\\' not in name and p.parts and p.parts[0]==TOOL_ID,'Unsafe archive path')
 return PurePosixPath(*p.parts[1:]).as_posix() if len(p.parts)>1 else ''
def verify(path):
 seen={''};digests={};index=None;links={};metadata={}
 with tarfile.open(path,'r|gz') as tar:
  for m in tar:
   relative=safe_name(m.name)
   require(relative not in seen,'Duplicate archive member');seen.add(relative)
   require(not excluded(relative),'Generated prefix/cache in archive')
   require(m.uid==m.gid==m.mtime==0 and not m.uname and not m.gname,'Noncanonical archive metadata')
   if m.isdir():continue
   if m.issym():
    require(not PurePosixPath(m.linkname).is_absolute() and '\\' not in m.linkname,'External symlink')
    target=posixpath.normpath(posixpath.join(posixpath.dirname(relative),m.linkname))
    require(target!='..' and not target.startswith('../'),'External symlink');links[relative]=m.linkname;continue
   require(m.isfile(),'Unsupported special archive member')
   with tar.extractfile(m) as f:
    if relative==INDEX:
     require(m.size<4*1024*1024,'Oversize checksum index');index=f.read().decode();continue
    digest=hashlib.sha256()
    for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
   digests[relative]=digest.hexdigest()
   if relative in {'compatibilitytool.vdf','toolmanifest.vdf','version'}:metadata[relative]=m.size
 require(index is not None,'Missing runtime checksum index')
 expected={}
 for line in index.splitlines():
  value,name=line.split('  ',1);require(name not in expected and len(value)==64,'Invalid checksum index');expected[name]=value
 require(expected==digests,'Runtime file hashes or indexed file set differ')
 for name,want in COMPONENTS.items():require(digests.get(name)==want,'Unexpected Wine/FEX component: '+name)
 def resolved(name):
  pending=name.split('/');done=[];hops=0
  while pending:
   part=pending.pop(0)
   if part in {'','.'}:continue
   if part=='..':
    require(bool(done),'External symlink chain');done.pop();continue
   candidate='/'.join(done+[part])
   if candidate in links:
    hops+=1;require(hops<=40,'Cyclic symlink chain')
    pending=links[candidate].split('/')+pending
   else:done.append(part)
  return '/'.join(done)
 require(all(resolved(name) in seen for name in links),'Dangling symlink')
 require(set(metadata)=={'compatibilitytool.vdf','toolmanifest.vdf','version'} and 'proton' in digests,'Missing Steam tool metadata')
 require('eso-bnet/source-manifest.json' in digests and 'RUNTIME-SOURCES.txt' in digests,'Missing source information')
 return {'regular_files_verified':len(digests),'symlinks_verified':len(links),'core_component_hashes_verified':True,'prefixes_and_caches_excluded':True}
if __name__=='__main__':print(json.dumps(verify(Path(sys.argv[1])),indent=2))
