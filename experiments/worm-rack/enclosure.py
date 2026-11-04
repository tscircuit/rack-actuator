"""Standard spur enclosure bounds and mounting datums, with a rear motor aperture."""
TRAY_NAME='Standard-size enclosure tray';COVER_NAME='Standard flat enclosure cover'
rect=ns['rect_cut'];wall=ns['CASE_WALL'];split=ns['CASE_SPLIT'];top=ns['CASE_TOP'];bottom=ns['CASE_BOTTOM']
old_left=ns['CASE_LEFT'];new_left=old_left;right=ns['CASE_RIGHT'];ymin=ns['CASE_YMIN'];ymax=ns['CASE_YMAX'];hood_top=top
tray=ns['tray'];cover=ns['cover']
# Close the downward-facing spur motor opening. Keep the complete shell envelope.
tray=tray.fuse(rect(-MOTOR_SIZE/2-1.1,MOTOR_SIZE/2+1.1,ns['MOTOR_Y']-MOTOR_SIZE/2-1.1,ns['MOTOR_Y']+MOTOR_SIZE/2+1.1,bottom,bottom+wall))
opening=rect(old_left-1,old_left+wall+1,MOTOR_Y-MOTOR_SIZE/2-1,MOTOR_Y+MOTOR_SIZE/2+1,MOTOR_Z-MOTOR_SIZE/2-1,MOTOR_Z+MOTOR_SIZE/2+1)
tray=tray.cut(opening);cover=cover.cut(opening)
for x in [old_left-1,right-wall-1]:
 access=xcyl(8.8,wall+2,x)
 tray=tray.cut(access);cover=cover.cut(access)
# Wider rack roof/underside teeth pass the front wall, above its mounting inserts.
portal=rect(right-wall-1,right+1,Y-5,ns['BACK_Y']+1,6,22)
tray=tray.cut(portal);cover=cover.cut(portal)
# The old rear wall clears the bridge if it crosses it, without moving any face.
tray=tray.cut(rect(old_left-1,old_left+wall+1,Y-12.5,Y+20.5,-30,-22))
# Broad floor-supported seats carry the motor bracket and both end bearings.
for x,y in REAR_SUPPORT_POINTS:
 tray=tray.fuse(cyl(5,-29-bottom,x,y,bottom)).fuse(rect(x-5,x+5,ymin,y+1,bottom,-29))
 tray=tray.cut(cyl(ns['INSERT_PILOT']/2,ns['INSERT_LENGTH']+.4,x,y,-29-ns['INSERT_LENGTH']-.4))
 ins=cyl(ns['INSERT_OD']/2,ns['INSERT_LENGTH'],x,y,-29-ns['INSERT_LENGTH']).cut(cyl(1.6,ns['INSERT_LENGTH'],x,y,-29-ns['INSERT_LENGTH']))
 parts.append(record(f'M3 rear motor support insert {x:g} {y:g}',ins,'#d4a54a','tray',embedded_host=TRAY_NAME))
 screw=cyl(1.45,10,x,y,-33).fuse(cyl(2.75,3,x,y,-23)).cut(cyl(1.25,2,x,y,-22))
 parts.append(record(f'M3x10 rear motor support screw {x:g} {y:g}',screw,'#a5b5c1','chassis_screws'))
for p in ns['parts']:
 if p['group'] in ['cover_screws','chassis_screws'] or p.get('embedded_host')=='05 Mounting enclosure tray':
  parts.append(record(p['name'],p['shape'],p['color'],p['group'],**({'embedded_host':TRAY_NAME} if p.get('embedded_host') else {})))
# Finish pilots after joining both support webs so neither web fills its neighbor's hole.
for x,y in REAR_SUPPORT_POINTS:tray=tray.cut(cyl(ns['INSERT_PILOT']/2,ns['INSERT_LENGTH']+.4,x,y,-29-ns['INSERT_LENGTH']-.4)).cut(cyl(3.55,4,x,y,-23))
# Clearance for the worm's initial downward disengagement, including the plain stem.
for a,b,r in [(WORM_START-.3,WORM_END+.3,STEM_RADIUS+.8),(GEAR_X-.8,GEAR_X+GEAR_WIDTH+.8,13.8),(-12.3,12.3,RA+.8)]:
 swept=xcyl(r,b-a,a).fuse(xcyl(r,b-a,a,Y,Z-7),box(b-a,2*r,7,((a+b)/2,Y,Z-3.5)))
 tray=tray.cut(swept)
# Axial service paths clear internal mounting webs as well as the end walls.
tray=tray.cut(xcyl(8.8,right+1-17.8,17.8))
tray=tray.cut(xcyl(MOTOR_TEETH/2+1.8,GEAR_X+GEAR_WIDTH-(old_left-1),old_left-1,MOTOR_Y,MOTOR_Z))
# Clear the motor body, including lower portions of the rear mounting posts.
# The top inserts retain their original positions on the supported upper webs.
tray=tray.cut(rect(MOTOR_REAR-1,MOTOR_FRONT+.8,MOTOR_Y-MOTOR_SIZE/2-.8,MOTOR_Y+MOTOR_SIZE/2+.8,MOTOR_Z-MOTOR_SIZE/2-.8,MOTOR_Z+MOTOR_SIZE/2+.8))
for y,z in motor_holes:tray=tray.cut(xcyl(3.55,22,MOTOR_FRONT-6,y,z))
tray=tray.clean();cover=cover.clean()
parts.extend([record(TRAY_NAME,tray,'#314959','tray',True),record(COVER_NAME,cover,'#d4dee5','cover',True)])
CASE_BOUNDS=[old_left,right,ymin,ymax,bottom,top]
MOUNTING={
 'reference':{'drive':'spur','enclosure':'enclosed','motor':args.motor,'stroke':STROKE},
 'top':{'xy':ns['CASE_CORNERS'],'planeZ':top,'thread':'M3'},
 'side':{'xz':ns['CASE_MOUNTS'],'planeY':ymax,'thread':'M3'},
 'front':{'yz':ns['FRONT_MOUNTS'],'planeX':right,'thread':'M3'},
 'output':{'xy':ns['OUTPUT_MOUNTS'],'planeZ':ns['OUTPUT_PAD_TOP'],'thread':'M3','throughDiameter':ns['OUTPUT_THROUGH_DIAMETER']},
 'originalCaseBounds':CASE_BOUNDS,'rearExtension':0,
 'note':'Enclosure bounds, mounting-hole centers and face planes match the enclosed spur actuator. Flat cover. Motor body projects through the rear aperture; allow room for its exposed back and controller.'}
