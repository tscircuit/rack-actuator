"""Extract actual Bambu G-code extrusion paths for an inspectable layer preview."""
import argparse,gzip,hashlib,json,math,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('output',type=Path);args=p.parse_args()
root=args.folder;raw=(root/'plate_1.gcode').read_bytes();result=json.loads((root/'result.json').read_text());plate=result['sliced_plates'][0]
assert result['return_code']==0 and plate['warning_message']=='',result
bbox=plate['objects'][0]['bbox'];dx=bbox['x']+36;dy=bbox['y']+40
layers=[];layer=None;role='Custom';x=y=z=e=0.;relative=True;absolute=True;extrusion={};counts={};regions={}
for line in raw.decode().splitlines():
 if line.startswith('; Z_HEIGHT:'):
  layer={'z':float(line.split(':')[1]),'paths':[[],[],[],[]]};layers.append(layer)
 if line.startswith('; FEATURE:'):role=line.split(':',1)[1].strip()
 code=line.split(';')[0].strip();cmd=code.split(' ',1)[0]
 if cmd=='M83':relative=True
 if cmd=='M82':relative=False
 if cmd=='G90':absolute=True
 if cmd=='G91':absolute=False
 if cmd not in ['G0','G1','G2','G3','G92']:continue
 values={k:float(v) for k,v in re.findall(r'([XYZE])([-+]?(?:\d*\.\d+|\d+))',code)}
 if cmd=='G92':
  e=values.get('E',e);continue
 nx=(values.get('X',x) if absolute else x+values.get('X',0));ny=(values.get('Y',y) if absolute else y+values.get('Y',0));nz=(values.get('Z',z) if absolute else z+values.get('Z',0))
 de=values.get('E',0) if relative else values.get('E',e)-e
 if 'E' in values:e=(e+de if relative else values['E'])
 if layer and de>0 and math.hypot(nx-x,ny-y)>.001 and role!='Custom':
  assert cmd not in ['G2','G3'],'Extruding arcs need tessellation'
  assert absolute,'Preview requires absolute XYZ'
  group=1 if role=='Support' else 2 if role=='Support interface' else 3 if role in ['Sparse infill','Internal solid infill','Gap infill'] else 0
  layer['paths'][group].extend(round(v,3) for v in [x-dx,y-dy,nx-dx,ny-dy])
  extrusion[role]=extrusion.get(role,0)+de;counts[role]=counts.get(role,0)+1
  if group in [1,2]:
   mx=(x+nx)/2-dx;my=(y+ny)/2-dy
   region='motor underside' if -1<=mx<=7 and nz<16 else 'adjustment shelves' if any(a<=mx<=b for a,b in [(42,69),(116,143)]) and 19<=abs(my)<=36 and nz<28 else 'side windows' if abs(my)>31 and 10<nz<44 else 'other bearing / lid features'
   regions[region]=regions.get(region,0)+de
 x,y,z=nx,ny,nz
factor=math.pi*(1.75/2)**2*1.27/1000
meta={'slicer':'Bambu Studio 2.9.1.70','gcode_sha256':hashlib.sha256(raw).hexdigest(),'stl_sha256':hashlib.sha256((root/'base.stl').read_bytes()).hexdigest(),'layer_count':len(layers),'layer_height_mm':.2,'estimated_seconds':plate['total_predication'],'estimated_grams':plate['filaments'][0]['total_used_g'],'support_grams':sum(v for k,v in extrusion.items() if k in ['Support','Support interface'])*factor,'support_regions_grams':{k:v*factor for k,v in regions.items()},'extrusion_segments':sum(counts.values()),'role_segments':counts,'role_filament_mm':extrusion,'model_translation_xy_mm':[dx,dy],'model_bounds_mm':[-36,155,-40,40,0,68],'profile':'P2S / 0.4 mm / Generic PETG / 0.20 mm / 4 walls / 25% gyroid / tree(auto), supports everywhere','region_note':'Support region totals classify deposited paths by position; they are not a topology or removability guarantee.'}
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(gzip.compress(json.dumps({'meta':meta,'layers':layers},separators=(',',':')).encode(),mtime=0));args.output.with_suffix('').with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta,indent=2))
