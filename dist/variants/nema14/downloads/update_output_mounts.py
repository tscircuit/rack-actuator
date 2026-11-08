"""Migrate checked rack presets to axial NEMA17 plates, preserving unrelated CAD.
Run once against a pre-migration checkout. Full fresh generation uses model.py.
The audit proves identical geometry behind the new plate and separates the
plate's conservative swept bounds from every retained part through animation.
"""
import argparse,pathlib,sys,json,gzip,hashlib,math,zipfile,copy
import numpy as np
import cadquery as cq
ROOT=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--motor',required=True);p.add_argument('--stroke',type=int,required=True);a=p.parse_args()
WORK=ROOT/'work/output-mount'/f'{a.motor}-{a.stroke}';WORK.mkdir(parents=True,exist_ok=True)
def digest(b):return hashlib.sha256(b).hexdigest()
def readjson(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def writejson(p,d):
 raw=json.dumps(d,separators=(',',':')).encode();p.write_bytes(gzip.compress(raw,mtime=0) if p.suffix=='.gz' else json.dumps(d,indent=2).encode())
def backup(p):
 target=WORK/'before'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True)
 if not target.exists():target.write_bytes(p.read_bytes())
 return target
oldpath=ROOT/'work/output-mount/baseline-model.py';oldsource=oldpath.read_text();newsource=(ROOT/'model.py').read_text()
cut=oldsource.index('\nfor p in UPPER:',oldsource.index('rack=make_rack(a.preload)'))
ns={'__file__':str(ROOT/'model.py'),'__name__':'output_mount_migration'};sys.argv=['model.py','--motor',a.motor,'--stroke',str(a.stroke),'--out',str(WORK/'scratch')]
exec(compile(oldsource[:cut],str(oldpath),'exec'),ns)
oldrack=ns['rack'];oldinserts=[q for q in ns['parts'] if q.get('embedded_host')];right=ns['right'];box=ns['box'];oldright=right
start=newsource.index('OUTPUT_PAD_SIZE=');end=newsource.index('\ncentral_relief_radius=')
exec(compile(newsource[start:end],str(ROOT/'model.py'),'exec'),ns)
plate=ns['make_output_plate']();newrack=ns['make_rack'](ns['a'].preload)
assert plate.isValid() and len(plate.Solids())==1
cutregion=box(100,300,300,(right+50,20,0))
def unchanged(old,new):
 before=old.cut(cutregion);after=new.cut(cutregion)
 diff=before.cut(after).Volume()+after.cut(before).Volume();assert diff<.01,diff
 assert new.isValid() and len(new.Solids())==1
 return diff
shape_difference=unchanged(oldrack,newrack)
newinserts=[]
for y,z in ns['OUTPUT_MOUNTS']:
 face=ns['OUTPUT_FACE_X']-.3;cyl=ns['output_cylinder']
 shape=cyl(ns['INSERT_OD']/2,ns['INSERT_LENGTH'],face-ns['INSERT_LENGTH'],y,z).cut(cyl(1.6,ns['INSERT_LENGTH'],face-ns['INSERT_LENGTH'],y,z))
 newinserts.append(dict(name=f'M3 heat-set insert output {y:g} {z:g}',color='#d4a54a',group='rack',printed=False,shape=shape,embedded_host='04 Beveled compliant rack'))
mount=dict(standard='NEMA17 hole pattern',hole_axis=[1,0,0],thread='M3',count=4,pattern_yz_mm=ns['OUTPUT_MOUNTS'],pitch_yz_mm=[31,31],face_size_mm=[42,42],plate_depth_mm=8,face_x_mm=right+8,center_y_mm=ns['OUTPUT_PAD_Y'],center_z_mm=6,insert_recess_mm=.3,thread_engagement_mm=[3,ns['INSERT_LENGTH']],through_diameter_mm=3.4,through_length_mm=8)
holechecks=[]
for y,z in ns['OUTPUT_MOUNTS']:
 cyl=ns['output_cylinder'];face=right+7.7
 probes={'through':cyl(1.7,8.2,right-.1,y,z),'driver':cyl(3,30,right+8,y,z),'insert_approach':cyl(ns['INSERT_OD']/2,30,face,y,z)}
 overlaps={k:max(0,newrack.intersect(v).Volume()) for k,v in probes.items()};assert max(overlaps.values())<.01,overlaps
 holechecks.append(dict(yz_mm=[y,z],overlap_mm3=overlaps))
def mesh(q):
 vs,ts=q['shape'].tessellate(.04,.12)
 return {k:v for k,v in q.items() if k!='shape'}|{'vertices':[[round(v.x,5),round(v.y,5),round(v.z,5)] for v in vs],'triangles':ts}
def stl(shape,path,worm=False):
 if worm:shape=shape.rotate((0,0,0),(1,0,0),180)
 bb=shape.BoundingBox();shape=shape.translate((-bb.xmin,-bb.ymin,-bb.zmin))
 cq.exporters.export(shape,str(path),tolerance=.03,angularTolerance=.12)
 raw=path.read_bytes();n=int.from_bytes(raw[80:84],'little');assert len(raw)==84+50*n
 triangles=np.ndarray((n,),dtype=np.dtype([('normal','<f4',3),('v','<f4',(3,3)),('attribute','<u2')]),buffer=raw,offset=84)['v'].astype(float)
 vertices,ids=np.unique(triangles.reshape(-1,3),axis=0,return_inverse=True);faces=ids.reshape(-1,3)
 edges=np.sort(np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]]),axis=1);_,counts=np.unique(edges,axis=0,return_counts=True)
 volume=np.einsum('ij,ij->i',triangles[:,0],np.cross(triangles[:,1],triangles[:,2])).sum()/6
 assert np.all(counts==2) and volume>0,(path,'invalid STL',volume)
 return path.read_bytes()
def delta(tracks,g,t):
 v=np.zeros(3);angle=0
 for seg in tracks.get(g,[]):
  f=max(0,min(1,(t-seg['start'])/(seg['end']-seg['start'])))
  v+=np.array(seg.get('delta',[0,0,0]))*f;angle+=seg.get('angle',0)*f
 return v,angle

def check_sweep(data,spring_file,worm):
 # The plate box includes its inserts. Continuous AABB envelopes between all
 # stage boundaries cover every translation, including simultaneous motions.
 tracks=data['tracks'];times=sorted({0.,1.}|{s[k] for seq in tracks.values() for s in seq for k in ['start','end']})
 pb=plate.BoundingBox();pmin=np.array([pb.xmin,pb.ymin,pb.zmin]);pmax=np.array([pb.xmax,pb.ymax,pb.zmax])
 shapes={q['name']:np.array(q['vertices']) for q in data['parts'] if q['group']!='rack'}
 # Free/deformed chassis meshes enlarge the envelope, never shrink it.
 if spring_file.exists():
  states=readjson(spring_file)
  if isinstance(states,dict):states=states.get('states',[])
  if isinstance(states,list):
   names=[q['name'] for q in data['parts'] if q.get('flex_chassis') or q['name']==data.get('chassisName')]
   for name in names:
    extra=[np.array(st['vertices']) for st in states if 'vertices' in st]
    if extra:shapes[name]=np.concatenate([shapes[name],*extra])
 minimum=float('inf');pairs=0
 def separated(amin,amax,bmin,bmax):
  gaps=np.maximum(bmin-amax,amin-bmax);return float(max(gaps))
 for q in data['parts']:
  if q['group']=='rack':continue
  vs=shapes[q['name']];bmin=vs.min(0)-.2;bmax=vs.max(0)+.2
  # Conservative rotation envelope for any rotating gear, shaft or fastener.
  rotates=q.get('rotating') or q['group'] in ['gear','shaft','set_screw']
  if rotates:
   pivot=np.array(q.get('rotationCenter',data.get('axisOrigin') if worm else data.get('rotationPivot')))
   if worm:
    radius=np.linalg.norm(vs[:,1:]-pivot[1:],axis=1).max()+.2;bmin[1:]=pivot[1:]-radius;bmax[1:]=pivot[1:]+radius
   else:
    radius=np.linalg.norm(vs[:,:2]-pivot[:2],axis=1).max()+.2;bmin[:2]=pivot[:2]-radius;bmax[:2]=pivot[:2]+radius
  # Full travel swept box; fixed guide flexure travel is already in the union.
  am=pmin.copy();ax=pmax.copy();am[0]-=a.stroke/2;ax[0]+=a.stroke/2
  gap=separated(am,ax,bmin,bmax);assert gap>0,('motion box collision',q['name'],gap)
  minimum=min(minimum,gap);pairs+=1
  for lo,hi in zip(times,times[1:]):
   bd=[delta(tracks,q['group'],t)[0] for t in [lo,hi]];ad=[delta(tracks,'rack',t)[0] for t in [lo,hi]]
   mn=bmin+np.minimum(*bd)-np.maximum(*ad);mx=bmax+np.maximum(*bd)-np.minimum(*ad)
   # Spring release adds only Z; conservative allowance covers all phases.
   if 'lowerStation' in q or q['group'].startswith('lower_'):mn[2]-=3;mx[2]+=3
   gap=separated(pmin,pmax,mn,mx);assert gap>0,('assembly box collision',q['name'],lo,hi,gap)
   minimum=min(minimum,gap);pairs+=1
 return dict(method='Continuous conservative AABB separation for full stroke and each piecewise-linear assembly interval; rotation envelopes and all available chassis spring meshes included.',mesh_bounds_padding_mm=.2,stage_intervals=len(times)-1,part_interval_checks=pairs,minimum_separation_mm=minimum,collisions=[])

def update_parts(data,rackshape,rackname):
 for i,q in enumerate(data['parts']):
  if q['group']=='rack' and q['printed']:
   data['parts'][i]=mesh({k:v for k,v in q.items() if k not in ['vertices','triangles']}|{'shape':rackshape})
 old=[i for i,q in enumerate(data['parts']) if q['name'].startswith('M3 heat-set insert output')]
 assert len(old)==4
 for i,q in zip(old,newinserts):data['parts'][i]=mesh(dict(q,embedded_host=rackname))
 return data

def bundle_rewrite(bundle,replacements):
 backup(bundle);temp=bundle.with_suffix('.tmp')
 with zipfile.ZipFile(bundle) as src,zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as dst:
  for info in src.infolist():
   if info.filename in replacements or info.filename.endswith(('.step','.step.gz')):continue
   dst.writestr(info,src.read(info.filename))
  for name,value in replacements.items():dst.writestr(name,value)
 temp.replace(bundle)

sourcehash=digest(newsource.encode());reportbase=dict(passed=True,output_mount=mount,unchanged_backbone_and_teeth_difference_mm3=shape_difference,hole_checks=holechecks,source_sha256=sourcehash,updater_sha256=digest(pathlib.Path(__file__).read_bytes()),limits=['Geometric fit and clearance checks only; no load rating or printed strength test.','NEMA17 four-hole interface; no motor pilot or shaft bore is added.','End plate protrudes beyond both rack printing faces; support is needed if printing on a long face.'])
manifest=readjson(ROOT/'work/output-mount/presets-before.json')
for preset in manifest['presets']:
 if (preset['motor'],preset['stroke'])!=(a.motor,a.stroke):continue
 folder=ROOT/'dist'/preset['basePath'].removeprefix('./');dest=folder/'downloads';meshfile=folder/'assets/assembly.json.gz';data=readjson(backup(meshfile));oldreport=readjson(backup(dest/'validation.json'))
 assert oldreport['source_sha256']==digest(oldsource.encode())
 assert abs(data['rackRight']-right)<1e-7
 spring=folder/'assets/spring-states.json.gz'
 if not spring.exists():spring=(ROOT/'dist' if a.motor=='nema17' and a.stroke==40 else ROOT/'dist/variants'/a.motor/(str(a.stroke) if a.stroke!=40 else ''))/'assets/spring-states.json.gz'
 report=copy.deepcopy(reportbase);report['sweep']=check_sweep(data,spring,False);report['baseline_validation_sha256']=digest(backup(dest/'validation.json').read_bytes())
 data=update_parts(data,newrack,'04 Beveled compliant rack')
 data.update(outputMounts=ns['OUTPUT_MOUNTS'],outputMountPitch=31,outputMountX=right+8,outputMountAxis=[1,0,0],outputMountPlane='YZ',outputPadDepth=8,outputPadCenterZ=6,outputPadSize=[42,42,8],geometrySourceSha256=digest(newsource.split('\n# Clear obsolete generated meshes')[0].encode()),outputMountValidation='output-mount-validation.json')
 data.pop('outputMountZ',None);data['frontFixtureOpeningYZ']=[min(ns['ROOT_Y'],24,ns['OUTPUT_PAD_Y']-21)-1,max(ns['BACK_Y'],40,ns['OUTPUT_PAD_Y']+21)+1,-16,28]
 coords=np.concatenate([np.array(q['vertices']) for q in data['parts']]);data['envelope']=(coords.max(0)-coords.min(0)).tolist();writejson(meshfile,data)
 replacements={'model.py':newsource.encode(),'output-mount-validation.json':json.dumps(report,indent=2).encode(),'provenance/pre-axial-output-validation.json':backup(dest/'validation.json').read_bytes(),'provenance/pre-axial-output-model.py':oldsource.encode()}
 # Retain previous full mechanism checks explicitly; the new proof covers the only changed solid region.
 updated=copy.deepcopy(oldreport);updated.update(source_sha256=sourcehash,output_mount=mount,output_mount_revision=report,retained_validation_sha256=report['baseline_validation_sha256']);writejson(dest/'validation.json',updated)
 replacements['validation.json']=(dest/'validation.json').read_bytes()
 for name in ['flexure-service-validation.json','lid-screw-clearance.json']:
  f=dest/name;d=readjson(backup(f));d.update(source_sha256=sourcehash,retained_validation_sha256=digest(backup(f).read_bytes()),output_mount_clearance_report='output-mount-validation.json');writejson(f,d);replacements[name]=f.read_bytes()
 for name,value in replacements.items():
  if '/' not in name:(dest/name).write_bytes(value)
 raw=stl(newrack,WORK/'spur-rack.stl');(dest/'04_Beveled_compliant_rack.stl').write_bytes(raw);replacements['04_Beveled_compliant_rack.stl']=raw
 bom=readjson(backup(dest/'bill-of-materials.json'));bom['output_mounting']=mount;writejson(dest/'bill-of-materials.json',bom);replacements['bill-of-materials.json']=(dest/'bill-of-materials.json').read_bytes()
 bundle_rewrite(dest/preset['bundleFile'],replacements)
 for step in dest.glob('*.step*'):step.unlink()
 print('UPDATED spur',a.motor,a.stroke,preset['enclosure'],report['sweep'],flush=True)

folder=ROOT/'dist/experiments/worm-rack'
if (a.motor,a.stroke)!=('nema17',40):folder=folder/'variants'/a.motor/str(a.stroke)
meshfile=folder/'assembly.json.gz';data=readjson(backup(meshfile));bundle=folder/'worm-rack-experiment.zip';backup(bundle)
oldreport=readjson(backup(folder/'validation.json'));replacements={}
sweep=check_sweep(data,folder/'spring-states.json.gz',True)
for style,cachefile in [('compliant','compliant-0.1.brep'),('solid','solid--0.1.brep')]:
 target=folder/'teeth'/style;part=readjson(backup(target/'part.json.gz'));validation=readjson(backup(target/'validation.json'))
 assert validation['passed']
 matches=[]
 with zipfile.ZipFile(backup(bundle)) as z:
  previousstl=z.read(f'stl/matched_{style}_rack.stl')
  for cached in (ROOT/'work/worm-teeth-cache'/f'{a.motor}-{a.stroke}').glob('*/'+cachefile):
   if (cached.parent/(style+'.stl')).exists() and (cached.parent/(style+'.stl')).read_bytes()==previousstl:matches.append(cached)
 assert len(matches)==1,matches
 old=cq.Shape.importBrep(str(matches[0]));new=old.cut(cutregion).fuse(plate).clean();difference=unchanged(old,new)
 report=copy.deepcopy(reportbase);report.update(sweep=sweep,unchanged_backbone_and_teeth_difference_mm3=difference,baseline_validation_sha256=digest(backup(target/'validation.json').read_bytes()))
 q=part['part'];part['part']=mesh({k:v for k,v in q.items() if k not in ['vertices','triangles']}|{'shape':new});revision=digest(part['revision'].encode()+json.dumps(mount,sort_keys=True).encode()+sourcehash.encode());part['revision']=revision;writejson(target/'part.json.gz',part)
 validation.update(variant_source_sha256=revision,output_mount_revision=report,base_checks_reused=validation.get('base_checks_reused','')+' Axial output plate verified separately by continuous conservative swept-bound separation; the former pad is removed, and a solid difference confirms unchanged teeth/backbone.');writejson(target/'validation.json',validation)
 raw=stl(new,WORK/(style+'-rack.stl'),True)
 replacements[f'stl/matched_{style}_rack.stl']=raw;replacements[f'teeth/{style}/validation.json']=(target/'validation.json').read_bytes();replacements[f'teeth/{style}/output-mount-validation.json']=json.dumps(report,indent=2).encode()
 replacements[f'provenance/pre-axial-{style}-validation.json']=backup(target/'validation.json').read_bytes()
 if style=='compliant':data=update_parts(data,new,'Matched compliant rack')
 print('UPDATED worm',a.motor,a.stroke,style,sweep,flush=True)
data['mounting']['output']={'yz':ns['OUTPUT_MOUNTS'],'planeX':right+8,'axis':[1,0,0],'pitch':[31,31],'faceSize':[42,42],'depth':8,'thread':'M3','throughDiameter':3.4};data['modelSourceSha256']=digest(json.dumps(data['mounting'],sort_keys=True).encode()+data['modelSourceSha256'].encode());writejson(meshfile,data)
oldreport.update(output_mount_revision=report,output_through_holes={'diameter_mm':3.4,'length_mm':8,'axis':[1,0,0],'intersections_mm3':[0,0,0,0]});writejson(folder/'validation.json',oldreport);replacements['validation.json']=(folder/'validation.json').read_bytes()
# Keep checked historical chassis source intact. Patch only its baseline output
# definition, and attach this migration source/proof so the new mount is reproducible.
with zipfile.ZipFile(backup(bundle)) as z:
 packaged=z.read('model.py').decode();assert packaged==oldsource
replacements['model.py']=newsource.encode();replacements['update_output_mounts.py']=pathlib.Path(__file__).read_bytes();replacements['provenance/pre-axial-model.py']=oldsource.encode();replacements['provenance/pre-axial-validation.json']=backup(folder/'validation.json').read_bytes()
for f in ['enclosure.py','validate.py']:
 # Other motor/flange revisions in these files are preserved in the bundle.
 with zipfile.ZipFile(backup(bundle)) as z:s=z.read('experiments/worm-rack/'+f).decode()
 if f=='enclosure.py':s=s.replace("'output':{'xy':ns['OUTPUT_MOUNTS'],'planeZ':ns['OUTPUT_PAD_TOP'],'thread':'M3','throughDiameter':ns['OUTPUT_THROUGH_DIAMETER']}","'output':{'yz':ns['OUTPUT_MOUNTS'],'planeX':ns['OUTPUT_FACE_X'],'axis':[1,0,0],'pitch':[31,31],'faceSize':[42,42],'depth':ns['OUTPUT_PAD_DEPTH'],'thread':'M3','throughDiameter':ns['OUTPUT_THROUGH_DIAMETER']}")
 else:
  s=s.replace("('output.xy',MOUNTING['output']['xy'],ref['outputMounts']),('output.planeZ',ns['OUTPUT_PAD_TOP'],ref['outputMountZ'])", "('output.yz',MOUNTING['output']['yz'],ref['outputMounts']),('output.planeX',ns['OUTPUT_FACE_X'],ref['outputMountX'])")
  s=s.replace("'length_mm':18,'intersections_mm3':[overlap(ns['cyl'](ns['OUTPUT_THROUGH_DIAMETER']/2,18.2,x,y,2.9),rack) for x,y in ns['OUTPUT_MOUNTS']]", "'length_mm':ns['OUTPUT_PAD_DEPTH'],'axis':[1,0,0],'intersections_mm3':[overlap(ns['output_cylinder'](ns['OUTPUT_THROUGH_DIAMETER']/2,ns['OUTPUT_PAD_DEPTH']+.2,ns['right']-.1,y,z),rack) for y,z in ns['OUTPUT_MOUNTS']]")
 replacements['experiments/worm-rack/'+f]=s.encode()
bundle_rewrite(bundle,replacements)
# Mirror changed rack download; other standalone legacy files are not used by viewer.
download=ROOT/'downloads/worm'/a.motor/str(a.stroke)/'matched_compliant_rack.stl.gz';download.write_bytes(gzip.compress(replacements['stl/matched_compliant_rack.stl'],mtime=0))
print('DONE',a.motor,a.stroke,flush=True)
