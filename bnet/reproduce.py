"""Exact post-link ESO corrections for pinned BNet1 Wine DLLs.

No game files are modified. Inputs remain intact; outputs require new paths.
Wine-derived changes retain LGPL-2.1-or-later terms.
"""
from pathlib import Path
import argparse,struct,json,hashlib

ROOT=Path(__file__).resolve().parent
KERNEL_IN='fed36267d61204658b96a976e4cf19ab1053c49a466ca58c2bde6089148773cb'
KERNEL_OUT='5b9c2d116f93a307e7b69c31544e52b7a5081fa7caa384020b1c09f948664d5b'
LAYOUTS={
 'bnet':dict(sha='e28f25f21ecf34a32ee2ce24672f023e436da08a88a01c6d4e93757633c9ba47',out='5da92139e0e34111acf952b4d7ba590da09d34fdb9e99b68086c6081bcda16ac',call=0xc9914,jump=0xc998c,end=0xf1204,map=0x13acad),
}
def require(value,message):
 if not value:raise ValueError(message)
def sha(b):return hashlib.sha256(b).hexdigest()
def pe_layout(b):
 pe=struct.unpack_from('<I',b,60)[0];require(b[pe:pe+4]==b'PE\0\0','PE signature')
 n=struct.unpack_from('<H',b,pe+6)[0];opt=struct.unpack_from('<H',b,pe+20)[0]
 sections=[struct.unpack_from('<IIII',b,pe+24+opt+40*i+8) for i in range(n)]
 def off(rva):
  for vs,va,rs,rp in sections:
   if va<=rva<va+rs:return rp+rva-va
  raise ValueError('Unmapped RVA')
 return pe,sections,off
def kernel(original):
 require(sha(original)==KERNEL_IN,'Unknown kernel32 baseline')
 b=bytearray(original);_,_,off=pe_layout(b)
 manifest=json.loads((ROOT/'kernel32-hotpatch-thunks.json').read_text())
 require(len(manifest['changes'])==796,'Kernel manifest size')
 for row in manifest['changes']:
  rva=int(row['rva'],16);pos=off(rva);old=bytes.fromhex(row['old']);new=bytes.fromhex(row['new'])
  require(bytes(b[pos:pos+16])==old,'Kernel original bytes')
  require(old[:2]==b'\xff\x25' and set(old[6:])<={0,204},'Kernel thunk shape')
  require(new[:10]==bytes.fromhex('488da42400000000ff25'),'Kernel prolog shape')
  require(rva+6+struct.unpack_from('<i',old,2)[0]==rva+14+struct.unpack_from('<i',new,10)[0],'Import target changed')
  b[pos:pos+16]=new
 require(sha(b)==KERNEL_OUT,'Kernel output hash')
 return b,manifest
def relative(pc,target,bits):
 delta=target-pc;require(delta%4==0 and -(1<<(bits+1))<=delta<(1<<(bits+1)),'Branch range')
 return (delta//4)&((1<<bits)-1)
def ntdll(original,variant):
 c=LAYOUTS[variant];require(sha(original)==c['sha'],'Unknown ntdll baseline')
 b=bytearray(original);pe,sections,off=pe_layout(b)
 call=c['call'];site=call+4;resume=call+8;jump=c['jump'];cave=(c['end']+15)&~15
 require(b[off(call):off(call)+16]==bytes.fromhex('700140f9510500581f0211eb41010054'),'Call checker bytes')
 require(b[off(jump):off(jump)+8]==bytes.fromhex('700140391ffe0371'),'Jump checker bytes')
 instruction=struct.unpack_from('<I',b,off(site))[0];imm=(instruction>>5)&0x7ffff
 if imm&0x40000:imm-=0x80000
 old_literal=site+imm*4
 require(b[off(old_literal):off(old_literal)+10]==bytes.fromhex('488bc448895820555de9'),'Fast-forward literal')
 imagebase=struct.unpack_from('<Q',b,pe+24+24)[0]
 lc=struct.unpack_from('<I',b,pe+24+112+80)[0]
 meta=struct.unpack_from('<Q',b,off(lc)+200)[0]-imagebase
 cm,cn=struct.unpack_from('<II',b,off(meta)+4)
 require(cn==3 and cm+8==c['map'],'Code map layout')
 ec_start,ec_size=struct.unpack_from('<II',b,off(cm+8));ec_base=ec_start&~3
 require(ec_start==0x83001 and ec_base+ec_size==c['end'],'ARM64EC range')
 require(off(cave+39)==off(cave)+39 and b[off(cave):off(cave)+40]==bytes(40),'Helper cave')
 require(cave+40<(struct.unpack_from('<I',b,off(cm+16))[0]&~3),'Next code range overlap')
 require(any(va<=cave and cave+40<=va+vs for vs,va,rs,rp in sections),'Helper outside mapped section')
 branch=lambda pc,target:0x14000000|relative(pc,target,26)
 load=lambda pc,target:0x58000011|(relative(pc,target,19)<<5)
 eq=lambda pc,target:0x54000000|(relative(pc,target,19)<<5)
 ins=[load(cave,cave+32),0xeb11021f,eq(cave+8,cave+24),load(cave+12,old_literal),branch(cave+16,resume),0xd503201f,0x9100216b,branch(cave+28,jump)]
 payload=struct.pack('<8I',*ins)+bytes.fromhex('488da42400000000')
 changes=[]
 for name,rva,new in [('call_checker_branch',site,struct.pack('<I',branch(site,cave))),('native_helper',cave,payload),('arm64ec_code_range_size',cm+12,struct.pack('<I',cave+40-ec_base))]:
  pos=off(rva);changes.append(dict(name=name,rva=hex(rva),file_offset=hex(pos),old=bytes(b[pos:pos+len(new)]).hex(),new=new.hex()));b[pos:pos+len(new)]=new
 require(len(b)==len(original),'File size changed')
 require(sha(b)==c['out'],'Ntdll output hash')
 return b,dict(input_sha256=sha(original),output_sha256=sha(b),helper_rva=hex(cave),resume_rva=hex(resume),jump_check_rva=hex(jump),original_literal_rva=hex(old_literal),changed_byte_count=sum(a!=c for a,c in zip(original,b)),changes=changes)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('variant',choices=LAYOUTS);p.add_argument('component',choices=['kernel32','ntdll']);p.add_argument('input',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
 require(a.input.resolve()!=a.output.resolve() and not a.output.exists(),'Separate new output required')
 result,manifest=kernel(a.input.read_bytes()) if a.component=='kernel32' else ntdll(a.input.read_bytes(),a.variant)
 with a.output.open('xb') as f:f.write(result)
 a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(variant=a.variant,component=a.component,sha256=sha(result))))
if __name__=='__main__':main()
