"""6805 housing with four shared NEMA17 screws and continuous side walls.

The rear-opening bearing tunnel clears the coupling and permits bearing loading.
Four M3x40 screws clamp the holder and wall directly to the motor's 31 mm pattern.
"""
import cadquery as cq

def make_holder(wall_front, bearing_back, bearing_front, front, center_z=42):
 def block(xa,xb,ya,yb,za,zb):
  return cq.Solid.makeBox(xb-xa,yb-ya,zb-za,cq.Vector(xa,ya,za))
 def bore(r,xa,xb,y=0,z=center_z):
  return cq.Solid.makeCylinder(r,xb-xa,cq.Vector(xa,y,z),cq.Vector(1,0,0))
 back=bearing_back-.1
 body=cq.Workplane(obj=block(back,front,-21.5,21.5,center_z-21.5,center_z+21.5)).edges('|X').fillet(4).val()
 centers=[(y,center_z+z) for y in [-15.5,15.5] for z in [-15.5,15.5]]
 columns=[]
 # Side shells connect the four corners; top and bottom stay open for the clamp.
 for sign in [-1,1]:
  ya,yb=sorted([12*sign,21.5*sign])
  side=cq.Workplane(obj=block(wall_front,front,ya,yb,center_z-21.5,center_z+21.5)).edges('|X').fillet(2).val()
  body=body.fuse(side)
  for dz in [-15.5,15.5]:
   column=block(wall_front,bearing_front,ya,yb,center_z+dz-4,center_z+dz+4)
   column=column.cut(bore(18.6,wall_front-1,bearing_front+1))
   columns.append(column.cut(bore(1.7,wall_front-1,front+1,sign*15.5,center_z+dz)))
 body=body.cut(bore(17.5,wall_front-1,front+1)).cut(bore(18.6,wall_front-1,bearing_front+.1))
 for y,z in centers:
  body=body.cut(bore(1.7,wall_front-1,front+1,y,z))
  # The 6 mm T8 wall needs a 2 mm recessed head seat. Both designs use M3x40
  # with the underside of the head at X34.3 and the tip at X-5.7.
  if front>34.3:body=body.cut(bore(2.95,34.3,front+1,y,z))
 return body.clean(),centers,columns

def inspect_load_path(holder,wall,front,bearing_front,columns,hardware,load_n=4.44822):
 """Geometric head seats and thread engagement, not FEA or a load rating."""
 def overlap(a,b):return max(0.,a.intersect(b).Volume())
 def annulus(ro,ri,x,length,y=0,z=42):
  return cq.Solid.makeCylinder(ro,length,cq.Vector(x,y,z),cq.Vector(1,0,0)).cut(cq.Solid.makeCylinder(ri,length,cq.Vector(x,y,z),cq.Vector(1,0,0)))
 lip=annulus(18.4,17.6,bearing_front+.1,front-bearing_front-.1)
 missing_lip=lip.cut(holder).Volume();missing_columns=[q.cut(holder).Volume() for q in columns]
 links=[]
 for bolt in hardware:
  b=bolt.BoundingBox();engagement=-b.xmin
  links.append(dict(holder_to_bolt_head_mm3=overlap(holder.translate((.1,0,0)),bolt),motor_thread_engagement_mm=engagement,passed=5.5<engagement<6 and overlap(holder.translate((.1,0,0)),bolt)>.1))
 return dict(passed=missing_lip<.01 and max(missing_columns)<.01 and len(links)==4 and all(q['passed'] for q in links),direction='+X, screw tip away from motor',continuous_lip_missing_mm3=missing_lip,continuous_columns_missing_mm3=missing_columns,shared_motor_bolts=links,mount_pattern_mm=[31,31],side_wall_minimum_mm=2.9,bearing_recess_to_bolt_bore_web_mm=(2*15.5**2)**.5-18.6-1.7,load_case_n=load_n,nominal_outer_race_contact_area_mm2=3.141592653589793*(18.5**2-17.5**2),nominal_average_seat_pressure_mpa=load_n/(3.141592653589793*(18.5**2-17.5**2)),limitations='Rigid abutment and nominal engagement checks do not establish motor thread strength/depth, plate bending, PETG layer strength, creep, fatigue, or tested capacity. Verify the actual motor permits 5.7 mm screw insertion; do not bottom out screws.')
