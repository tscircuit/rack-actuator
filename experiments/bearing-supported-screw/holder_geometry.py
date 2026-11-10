"""Outward-boss 6805 housing; reusable by the two independent Z prototypes.

Four continuous columns carry front mounting washers to the wall. Mounting
holes are outside the 43 mm bearing-seat body, on a 52 x 31 mm pattern.
No access slots cut the bearing plate or the columns.
"""
import cadquery as cq

def make_holder(wall_front, bearing_back, bearing_front, front, center_z=42):
 def block(xa,xb,ya,yb,za,zb):
  return cq.Solid.makeBox(xb-xa,yb-ya,zb-za,cq.Vector(xa,ya,za))
 def bore(r,xa,xb,y=0,z=center_z):
  return cq.Solid.makeCylinder(r,xb-xa,cq.Vector(xa,y,z),cq.Vector(1,0,0))
 back=bearing_back-.1
 body=cq.Workplane(obj=block(back,front,-21.5,21.5,center_z-21.5,center_z+21.5)).edges('|X').fillet(4).val()
 centers=[(y,center_z+z) for y in [-26.,26.] for z in [-15.5,15.5]]
 columns=[]
 for y,z in centers:
  ya,yb=sorted([20*(1 if y>0 else -1),31*(1 if y>0 else -1)])
  column=cq.Workplane(obj=block(wall_front,front,ya,yb,z-5.5,z+5.5)).edges('|X').fillet(2).val()
  body=body.fuse(column);columns.append(column.cut(bore(1.7,wall_front-1,front+1,y,z)))
 body=body.cut(bore(17.5,wall_front-1,front+1)).cut(bore(18.6,wall_front-1,bearing_front+.1))
 for y,z in centers:body=body.cut(bore(1.7,wall_front-1,front+1,y,z))
 return body.clean(),centers,columns

def axial_locknut(x,y,z):
 return cq.Workplane('YZ',origin=(x,y,z)).polygon(6,5.5/(3**.5/2)).extrude(4).val().cut(cq.Solid.makeCylinder(1.55,4.2,cq.Vector(x-.1,y,z),cq.Vector(1,0,0)))

def inspect_load_path(holder,wall,front,bearing_front,columns,hardware,load_n=4.44822):
 """Geometric abutments and average stress only, not FEA or a load rating."""
 def overlap(a,b):return max(0.,a.intersect(b).Volume())
 def annulus(ro,ri,x,length,y=0,z=42):
  return cq.Solid.makeCylinder(ro,length,cq.Vector(x,y,z),cq.Vector(1,0,0)).cut(cq.Solid.makeCylinder(ri,length,cq.Vector(x,y,z),cq.Vector(1,0,0)))
 lip=annulus(18.4,17.6,bearing_front+.1,front-bearing_front-.1)
 missing_lip=lip.cut(holder).Volume();missing_columns=[q.cut(holder).Volume() for q in columns]
 links=[]
 for bolt,front_washer,rear_washer,nut in hardware:
  links.append(dict(holder_to_front_washer=overlap(holder.translate((.1,0,0)),front_washer),front_washer_to_nut=overlap(front_washer.translate((.1,0,0)),nut),bolt_head_to_rear_washer=overlap(bolt.translate((.1,0,0)),rear_washer),rear_washer_to_wall=overlap(rear_washer.translate((.1,0,0)),wall)))
 column_areas=[q.Volume()/q.BoundingBox().xlen for q in columns]
 return dict(passed=missing_lip<.01 and max(missing_columns)<.01 and all(min(q.values())>.1 for q in links),direction='+X, screw tip away from motor',continuous_lip_missing_mm3=missing_lip,continuous_columns_missing_mm3=missing_columns,abutment_overlap_checks_mm3=links,column_net_areas_mm2=column_areas,minimum_bolt_hole_edge_web_mm=3.3,load_case_n=load_n,nominal_outer_race_contact_area_mm2=3.141592653589793*(18.5**2-17.5**2),nominal_average_seat_pressure_mpa=load_n/(3.141592653589793*(18.5**2-17.5**2)),limitations='Average contact pressure and rigid abutment checks do not establish plate bending strength, bolt preload, printed PETG layer strength, creep, fatigue, or tested load capacity.')
