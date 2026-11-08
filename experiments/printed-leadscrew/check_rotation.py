"""Supplement CAD checks with a complete revolution against stationary parts.

Usage: python experiments/printed-leadscrew/check_rotation.py ASSET_DIRECTORY
Reads the exported viewer meshes; the main CAD validator separately checks the
moving carriage, thread clearance and exploded assembly. No collision waivers.
"""
import argparse,gzip,json,math,pathlib
import fcl
import numpy as np

def check(directory):
 data=json.loads(gzip.decompress((directory/'assembly.json.gz').read_bytes()))
 assert data['printedDrive'] and data.get('shaftClamp'), 'Requires bolt/nut D-shaft geometry'
 parts=data['parts'];models=[]
 for p in parts:
  m=fcl.BVHModel();m.beginModel(len(p['vertices']),len(p['triangles']))
  m.addSubModel(np.array(p['vertices']),np.array(p['triangles'],dtype=np.int32));m.endModel()
  models.append(fcl.CollisionObject(m))
 rotors=[i for i,p in enumerate(parts) if p['group']=='rotor']
 fixed=[i for i,p in enumerate(parts) if p['group'] not in ['rotor','carriage']]
 pivot=np.array(data['axisOrigin']);hits=[]
 for degrees in range(0,360,5):
  angle=math.radians(degrees);c,s=math.cos(angle),math.sin(angle)
  rotation=np.array([[1,0,0],[0,c,-s],[0,s,c]])
  for i in rotors:
   models[i].setTransform(fcl.Transform(rotation,pivot-rotation@pivot))
   for j in fixed:
    if fcl.collide(models[i],models[j],fcl.CollisionRequest(),fcl.CollisionResult()):
     hits.append(dict(angle_degrees=degrees,parts=[parts[i]['name'],parts[j]['name']]))
 return dict(passed=not hits,width_multiple=data['widthMultiple'],model_source_sha256=data['modelSourceSha256'],samples=72,angular_increment_degrees=5,collisions=hits,method='Supplementary exported-triangle collision check: every rotor against every stationary part over one complete revolution. Moving-carriage and disassembly checks are in validation.json.')

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('assets',type=pathlib.Path);args=parser.parse_args()
 result=check(args.assets);print(json.dumps(result,indent=2));assert result['passed'],result
