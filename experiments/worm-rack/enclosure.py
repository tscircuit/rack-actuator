"""Enclosure and mounting interfaces, executed by the worm family model.
Preserve the corresponding fully enclosed spur model's mounting datums.
A rear extension encloses the axial motor, leaving its back face 4 mm exposed.
"""
TRAY_NAME='Mount-compatible enclosure tray';COVER_NAME='Raised removable enclosure cover'
rect=ns['rect_cut'];wall=ns['CASE_WALL'];split=ns['CASE_SPLIT'];top=ns['CASE_TOP'];bottom=ns['CASE_BOTTOM']
old_left=ns['CASE_LEFT'];right=ns['CASE_RIGHT'];ymin=ns['CASE_YMIN'];ymax=ns['CASE_YMAX']
new_left=MOTOR_REAR+4.;hood_right=32.;hood_ymax=Y+MOTOR_SIZE/2+4.8
hood_top=bracket_top+1.2+wall
tray=ns['tray'];cover=ns['cover']
# Seal the spur motor's underside opening; only the axial motor's rear is exposed.
tray=tray.fuse(rect(-MOTOR_SIZE/2-1.1,MOTOR_SIZE/2+1.1,ns['MOTOR_Y']-MOTOR_SIZE/2-1.1,ns['MOTOR_Y']+MOTOR_SIZE/2+1.1,bottom,bottom+wall))
# Extend the original shell rearward; mounting posts remain at the original datums.
tray=tray.fuse(rect(new_left,old_left+wall,ymin,ymax,bottom,split).cut(rect(new_left+wall,old_left+wall+1,ymin+wall,ymax-wall,bottom+wall,split+1)))
cover=cover.fuse(rect(new_left,old_left+wall,ymin,ymax,split+.4,top).cut(rect(new_left+wall,old_left+wall+1,ymin+wall,ymax-wall,split,top-wall)))
# Remove the former rear wall; retain the floor, side walls, posts and their webs.
tray=tray.cut(rect(old_left-.1,old_left+wall+.1,ymin+wall,ymax-wall,bottom+wall,split+1))
cover=cover.cut(rect(old_left-.1,old_left+wall+.1,ymin+wall,ymax-wall,split,top-wall))
# A raised hood covers the worm, integral motor bracket and full motor body.
cover=cover.fuse(rect(new_left,hood_right,ymin,hood_ymax,top-wall,hood_top))
cover=cover.cut(rect(new_left+wall,hood_right-wall,ymin+wall,hood_ymax-wall,top-wall,hood_top-wall))
# Open the old lid ceiling under the hood while retaining existing screw seats.
# The cut starts at the old ceiling's inner face; the recessed head seats lie below it.
# The motor aperture crosses both shell halves and is open during cover removal.
motor_opening=rect(new_left-1,new_left+wall+1,Y-MOTOR_SIZE/2-1,Y+MOTOR_SIZE/2+1,Z-MOTOR_SIZE/2-1,Z+MOTOR_SIZE/2+1)
tray=tray.cut(motor_opening);cover=cover.cut(motor_opening)
# Clear the lower-front motor screw head as it leaves the bracket. This only
# relieves the inside of the nearby top post, away from its insert bore.
tray=tray.cut(xcyl(3.35,30,MOTOR_FRONT+4,Y-MOTOR_PITCH/2,Z-MOTOR_PITCH/2))
# The low former rear wall also needs clearance where the chassis bridge passes.
bridge_clear=rect(old_left-1,old_left+wall+1,Y-12.5,Y+8,-30,-22)
tray=tray.cut(bridge_clear)
# Tie the former rear/front lid boss to the side wall after opening the rear wall.
for x,y in ns['COVER_SEATS']:
 if abs(x-(old_left+7.5))<1e-6 and y<Y:
  cover=cover.fuse(rect(x,x+12,y-2,y+2,split+.4,top-wall))
  cover=cover.fuse(rect(x+10,x+14,ymin,y+2,split+.4,top-wall))
# Existing mounting posts and lid screws remain accessible through the raised roof.
for x,y in ns['CASE_CORNERS']:
 cover=cover.cut(cyl(5.4,hood_top-split+2,x,y,split-1))
 x0,x1=(old_left-1,x) if x<ns['CASE_CENTER'][0] else (x,right+1)
 cover=cover.cut(rect(x0,x1,y-5.4,y+5.4,split-1,top+.1))
for x,y in ns['COVER_SEATS']:
 cover=cover.cut(cyl(1.7,hood_top-split+2,x,y,split-1))
 cover=cover.cut(cyl(3.1,hood_top-top+5,x,y,top-3.3))
# Open-bottom stem clearance also permits vertical lid removal. The raised roof stays intact.
cover=cover.cut(rect(WORM_START-.8,-11,Y-STEM_RADIUS-.8,Y+STEM_RADIUS+.8,split-1,top+.1))
# The rear extension uses an additional cover screw on its far-side rail, clear of motor.
# Keep their seats at the same height as the original lid; the hood is on the other side.
extra_seats=[(new_left+8,ymax-8)]
for x,y in extra_seats:
 tray=tray.fuse(cyl(4.5,split-bottom,x,y,bottom)).fuse(rect(x-4.5,x+4.5,y,ymax,bottom,split))
 cover=cover.fuse(cyl(4.5,top-split-.4,x,y,split+.4)).fuse(rect(x-4.5,x+4.5,y,ymax,split+.4,top))
 tray=tray.cut(cyl(ns['INSERT_PILOT']/2,ns['INSERT_LENGTH']+.4,x,y,split-ns['INSERT_LENGTH']-.4))
 insert=cyl(ns['INSERT_OD']/2,ns['INSERT_LENGTH'],x,y,split-ns['INSERT_LENGTH']).cut(cyl(1.6,ns['INSERT_LENGTH'],x,y,split-ns['INSERT_LENGTH']))
 parts.append(record('M3 rear extension lid insert',insert,'#d4a54a','tray',embedded_host=TRAY_NAME))
 cover=cover.cut(cyl(1.7,top-split+1,x,y,split)).cut(cyl(3.1,4.3,x,y,top-3.3))
 head_z=top-3.3
 screw=cyl(1.45,20,x,y,head_z-20).fuse(cyl(2.75,3,x,y,head_z)).cut(cyl(1.25,2,x,y,head_z+1))
 parts.append(record('M3x20 rear extension lid screw',screw,'#a5b5c1','cover_screws'))
# A broad, floor- and wall-connected rear platform carries the motor's weight.
# It avoids a long unsupported chassis bridge on the 100/150 mm versions.
tray=tray.fuse(rect(MOTOR_FRONT+6,MOTOR_FRONT+18,ymin,Y+7.5,bottom,-29))
for x,y in REAR_SUPPORT_POINTS:
 tray=tray.cut(cyl(ns['INSERT_PILOT']/2,ns['INSERT_LENGTH']+.4,x,y,-29-ns['INSERT_LENGTH']-.4))
 support_insert=cyl(ns['INSERT_OD']/2,ns['INSERT_LENGTH'],x,y,-29-ns['INSERT_LENGTH']).cut(cyl(1.6,ns['INSERT_LENGTH'],x,y,-29-ns['INSERT_LENGTH']))
 parts.append(record(f'M3 rear motor support insert {x:g} {y:g}',support_insert,'#d4a54a','tray',embedded_host=TRAY_NAME))
 support_screw=cyl(1.45,10,x,y,-33).fuse(cyl(2.75,3,x,y,-23)).cut(cyl(1.25,2,x,y,-22))
 parts.append(record(f'M3x10 rear motor support screw {x:g} {y:g}',support_screw,'#a5b5c1','chassis_screws'))
for p in ns['parts']:
 if p['group'] in ['cover_screws','chassis_screws'] or (p.get('embedded_host')=='05 Mounting enclosure tray'):
  parts.append(record(p['name'],p['shape'],p['color'],p['group'],**({'embedded_host':TRAY_NAME} if p.get('embedded_host') else {})))
tray=tray.clean();cover=cover.clean()
parts.extend([record(TRAY_NAME,tray,'#314959','tray',True),record(COVER_NAME,cover,'#d4dee5','cover',True)])
CASE_BOUNDS=[new_left,right,ymin,ymax,bottom,hood_top]
MOUNTING={
 'reference':{'drive':'spur','enclosure':'enclosed','motor':args.motor,'stroke':STROKE},
 'top':{'xy':ns['CASE_CORNERS'],'planeZ':top,'thread':'M3'},
 'side':{'xz':ns['CASE_MOUNTS'],'planeY':ymax,'thread':'M3'},
 'front':{'yz':ns['FRONT_MOUNTS'],'planeX':right,'thread':'M3'},
 'output':{'xy':ns['OUTPUT_MOUNTS'],'planeZ':ns['OUTPUT_PAD_TOP'],'thread':'M3','throughDiameter':ns['OUTPUT_THROUGH_DIAMETER']},
 'originalCaseBounds':[old_left,right,ymin,ymax,bottom,top],
 'raisedCoverClearance':{'xmin':new_left,'xmax':hood_right,'ymin':ymin,'ymax':hood_ymax,'zmax':hood_top},
 'rearExtension':old_left-new_left,
 'note':'Same hole centers and face planes as the matching enclosed spur actuator. Top mounting hardware must clear the raised hood; a solid flat plate requires a cutout. Motor rear face projects 4 mm outside the rear aperture.'}
