# Pinned rack geometry; lead-screw retention is developed independently.
def snap_local(c,u):return cq.Plane(origin=c,xDir=(1,0,0),normal=u)
def local_box(c,u,xa,xb,ya,yb,ta,tb):
 return cq.Workplane(snap_local(c,u)).center((xa+xb)/2,(ya+yb)/2).workplane(offset=ta).rect(xb-xa,yb-ya).extrude(tb-ta).val()
def snap_pin(c,u,compression=0):
 # Ø4.8 shaft, two opposing retaining ears and a rounded-ended 1.2 mm slot.
 # Only the ears protrude beyond the bearing bore, allowing inward flex in X.
 shaft=cyl(2.4,15.25,c,u,-2.75)
 head=cyl(2.8,.35,c,u,-3.1).fuse(cq.Solid.makeCone(2.3,2.8,1.3,cq.Vector(*at(c,u,-4.4)),cq.Vector(*u)))
 head=head.intersect(local_box(c,u,-3,3,-1.5,1.5,-4.5,-2.7))
 pin=shaft.fuse(head)
 slot=local_box(c,u,-.6,.6,-4,4,-4.5,9)
 v=snap_local(c,u).yDir.toTuple()
 slot=slot.fuse(cyl(.6,8,at(at(c,u,9),v,-4),v))
 pin=pin.cut(slot).clean()
 if not compression:return pin
 # Schematic elastic deflection: each prong shears toward the slot, zero at
 # its root. It is an assembly clearance model, not a PETG stress simulation.
 result=pin.intersect(local_box(c,u,-4,4,-4,4,9.6,13))
 for sign in [-1,1]:
  half=pin.intersect(local_box(c,u,-4 if sign<0 else 0,0 if sign<0 else 4,-4,4,-5,9.6))
  k=sign*compression/(9.6+2.75);offset=-k*(9.6+sum(c[i]*u[i] for i in range(3)))
  matrix=cq.Matrix([[1,k*u[1],k*u[2],offset],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
  result=result.fuse(half.transformGeometry(matrix))
 return result.clean()
def inner_race_seat(shape,c,u):
 # Ø7.8 fixed inner-race land; a deep pin clearance frees the split prongs.
 # Open the entire Ø17 bearing insertion corridor, removing the former lip.
 start=-12 if abs(u[2])<.01 else -25
 result=shape.cut(cyl(8.5,4.5-start,c,u,start)).fuse(cyl(3.9,2.6,c,u,2.5))
 return result.cut(cyl(2.7,8.5,c,u,2.5)).clean()
