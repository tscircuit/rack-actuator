"""Standard spur enclosure bounds and mounting datums, with a rear motor aperture."""
TRAY_NAME='Standard-size enclosure tray';COVER_NAME='Standard flat enclosure cover'
rect=ns['rect_cut'];wall=ns['CASE_WALL'];split=ns['CASE_SPLIT'];top=ns['CASE_TOP'];bottom=ns['CASE_BOTTOM']
old_left=ns['CASE_LEFT'];new_left=old_left;right=ns['CASE_RIGHT'];ymin=ns['CASE_YMIN'];ymax=ns['CASE_YMAX'];hood_top=top
tray=ns['tray'];cover=ns['cover']
# Close the downward-facing spur motor opening. Keep the complete shell envelope.
tray=tray.fuse(rect(-MOTOR_SIZE/2-1.1,MOTOR_SIZE/2+1.1,ns['MOTOR_Y']-MOTOR_SIZE/2-1.1,ns['MOTOR_Y']+MOTOR_SIZE/2+1.1,bottom,bottom+wall))
opening=rect(old_left-1,old_left+wall+1,MOTOR_Y-MOTOR_SIZE/2-1,MOTOR_Y+MOTOR_SIZE/2+1,MOTOR_Z-MOTOR_SIZE/2-1,MOTOR_Z+MOTOR_SIZE/2+1)
tray=tray.cut(opening);cover=cover.cut(opening)
# The lowered rack and the M5 end-bolt service port share the front opening.
portal=rect(right-wall-1,right+1,Y-4.8,ns['BACK_Y']+1,Z+7.2,22)
tray=tray.cut(portal).cut(xcyl(6.2,wall+2,right-wall-1));cover=cover.cut(portal)
# Broad floor-supported seats carry the motor bracket and the single end bearing.
for x,y in REAR_SUPPORT_POINTS:
 tray=tray.fuse(cyl(5,SUPPORT_PAD_BOTTOM-bottom,x,y,bottom)).fuse(rect(x-5,x+5,ymin,y+1,bottom,SUPPORT_PAD_BOTTOM))
 tray=tray.cut(cyl(ns['INSERT_PILOT']/2,ns['INSERT_LENGTH']+.4,x,y,SUPPORT_PAD_BOTTOM-ns['INSERT_LENGTH']-.4))
 ins=cyl(ns['INSERT_OD']/2,ns['INSERT_LENGTH'],x,y,SUPPORT_PAD_BOTTOM-ns['INSERT_LENGTH']).cut(cyl(1.6,ns['INSERT_LENGTH'],x,y,SUPPORT_PAD_BOTTOM-ns['INSERT_LENGTH']))
 parts.append(record(f'M3 rear motor support insert {x:g} {y:g}',ins,'#d4a54a','tray',embedded_host=TRAY_NAME))
 screw=cyl(1.45,8,x,y,SUPPORT_PAD_TOP-8).fuse(cyl(2.75,3,x,y,SUPPORT_PAD_TOP)).cut(cyl(1.25,2,x,y,SUPPORT_PAD_TOP+1))
 parts.append(record(f'M3x8 rear motor support screw {x:g} {y:g}',screw,'#a5b5c1','chassis_screws'))
for p in ns['parts']:
 if p['group'] in ['cover_screws','chassis_screws'] or p.get('embedded_host')=='05 Mounting enclosure tray':
  parts.append(record(p['name'],p['shape'],p['color'],p['group'],**({'embedded_host':TRAY_NAME} if p.get('embedded_host') else {})))
# Finish pilots after joining both support webs.
for x,y in REAR_SUPPORT_POINTS:tray=tray.cut(cyl(ns['INSERT_PILOT']/2,ns['INSERT_LENGTH']+.4,x,y,SUPPORT_PAD_BOTTOM-ns['INSERT_LENGTH']-.4)).cut(cyl(3.55,30,x,y,SUPPORT_PAD_TOP))
# Clearance for rearward motor/worm withdrawal. The retained bearing stays put.
tray=tray.cut(xcyl(RA+.8,WORM_END+.3-(old_left-1),old_left-1))
tray=tray.cut(rack_channel(-WARP_END-STROKE/2-1,right+1))
# Broad integral pedestal and front axial stop: no keeper or extra printed part.
tray=tray.fuse(rect(14,26.15,Y-11.2,Y+11.2,bottom,Z-12))
retainer=rect(23.15,26.15,Y-10,Y+10,bottom,Z+10).cut(xcyl(6,3.2,23.05))
tray=tray.fuse(retainer).cut(rack_channel(14,right+1))
# Open M5 access continues through any existing mounting webs to the front face.
tray=tray.cut(xcyl(6.2,right+1-26.15,26.15))
# Clear the motor body, including lower portions of the rear mounting posts.
# The top inserts retain their original positions on the supported upper webs.
tray=tray.cut(rect(MOTOR_REAR-1,MOTOR_FRONT+.8,MOTOR_Y-MOTOR_SIZE/2-.8,MOTOR_Y+MOTOR_SIZE/2+.8,MOTOR_Z-MOTOR_SIZE/2-.8,MOTOR_Z+MOTOR_SIZE/2+.8))
for y,z in motor_holes:tray=tray.cut(xcyl(3.55,22,MOTOR_FRONT-6,y,z))
tray=clear_motor_service(tray)
tray=tray.clean();cover=cover.clean()
parts.extend([record(TRAY_NAME,tray,'#314959','tray',True),record(COVER_NAME,cover,'#d4dee5','cover',True)])
CASE_BOUNDS=[old_left,right,ymin,ymax,bottom,top]
MOUNTING={
 'reference':{'drive':'spur','enclosure':'enclosed','motor':args.motor,'stroke':STROKE},
 'top':{'xy':ns['CASE_CORNERS'],'planeZ':top,'thread':'M3'},
 'side':{'xz':ns['CASE_MOUNTS'],'planeY':ymax,'thread':'M3'},
 'front':{'yz':ns['FRONT_MOUNTS'],'planeX':right,'thread':'M3'},
 'output':{'yz':ns['OUTPUT_MOUNTS'],'planeX':ns['OUTPUT_FACE_X'],'axis':[1,0,0],'pitch':[31,31],'faceSize':[42,42],'depth':ns['OUTPUT_PAD_DEPTH'],'thread':'M3','throughDiameter':ns['OUTPUT_THROUGH_DIAMETER']},
 'originalCaseBounds':CASE_BOUNDS,'rearExtension':0,
 'note':'Enclosure bounds, mounting-hole centers and face planes match the enclosed spur actuator. Flat cover. Motor body projects through the rear aperture; allow room for its exposed back and controller.'}
