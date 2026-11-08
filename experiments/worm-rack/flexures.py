"""18 mm spring floors with 5 mm unloaded end blends.
Executed in the baseline CadQuery namespace before chassis construction.
Loaded shapes use a prescribed, volume-preserving vertical displacement; not FEA.
"""
LEAF_LENGTH=18.
ROOT_BLEND_RADIUS=5.
CARRIER_BLEND_RADIUS=5.
FRONT_BLEND_RADIUS=2.
SPRING_ROOT_OFFSET=LEAF_LENGTH+5
LEAF_OFFSET=LEAF_LENGTH+9

def leaf_profile(deflection,carrier_blend=False):
 x0=4.;x1=x0+LEAF_LENGTH;end_x=x1+10;top=-27+SPRING_THICKNESS
 def drop(x):
  u=max(0,min(1,(x-x0)/LEAF_LENGTH));return deflection*(3*u*u-2*u*u*u)
 def slope(x):
  u=max(0,min(1,(x-x0)/LEAF_LENGTH));return -deflection*6*u*(1-u)/LEAF_LENGTH
 def v(x,z):return cq.Vector(x,0,z)
 def line(a,b):return cq.Edge.makeLine(v(*a),v(*b))
 def beam(a,b,z):
  if not deflection:return line((a,z),(b,z))
  dx=(b-a)/3
  return cq.Edge.makeBezier([v(a,z-drop(a)),v(a+dx,z-drop(a)+dx*slope(a)),v(b-dx,z-drop(b)-dx*slope(b)),v(b,z-drop(b))])
 def round_edge(kind):
  r=ROOT_BLEND_RADIUS if kind=='root' else CARRIER_BLEND_RADIUS
  def sample(t):
   if kind=='root':x=x0+r-r*math.cos(t);z=top+r-r*math.sin(t);dx=r*math.sin(t);dz=-r*math.cos(t)
   else:x=x1-r+r*math.sin(t);z=top+r-r*math.cos(t);dx=r*math.cos(t);dz=r*math.sin(t)
   return v(x,z-drop(x)),v(dx,dz+slope(x)*dx)
  if not deflection:return cq.Edge.makeThreePointArc(sample(0)[0],sample(math.pi/4)[0],sample(math.pi/2)[0])
  ts=[math.pi/2*k/40 for k in range(41)]
  return cq.Edge.makeSpline([sample(t)[0] for t in ts],tangents=[sample(0)[1],sample(math.pi/2)[1]],parameters=ts,scale=False,tol=1e-8)
 end=x1-CARRIER_BLEND_RADIUS if carrier_blend else x1
 edges=[line((3,top+ROOT_BLEND_RADIUS),(x0,top+ROOT_BLEND_RADIUS)),round_edge('root'),beam(x0+ROOT_BLEND_RADIUS,end,top)]
 if carrier_blend:
  edges+=[round_edge('carrier'),line((x1,top+CARRIER_BLEND_RADIUS-deflection),(end_x,top+CARRIER_BLEND_RADIUS-deflection)),line((end_x,top+CARRIER_BLEND_RADIUS-deflection),(end_x,-27-deflection))]
 else:edges += [line((x1,top-deflection),(end_x,top-deflection)),line((end_x,top-deflection),(end_x,-27-deflection))]
 edges += [line((end_x,-27-deflection),(x1,-27-deflection)),beam(x1,x0,-27),line((x0,-27),(3,-27)),line((3,-27),(3,top+ROOT_BLEND_RADIUS))]
 return cq.Wire.assembleEdges(edges)

def spring_seat(spec,deflection):
 x=spec['x'];y=spec['center'][1];free_z=-17+SPRING_PRELOAD;body_width=43.5-y-BODY_FRONT
 rear=cq.Solid.extrudeLinear(leaf_profile(deflection,True),[],cq.Vector(0,-body_width,0)).translate((0,43.5,0))
 front=cq.Solid.extrudeLinear(leaf_profile(deflection),[],cq.Vector(0,-(FLOOR_WIDTH-body_width),0)).translate((0,43.5-body_width,0))
 leaf=rear.fuse(front).clean()
 if x<0:leaf=leaf.mirror('YZ')
 leaf=leaf.translate((x-math.copysign(LEAF_OFFSET,x),0,0))
 body=box(10,body_width,16.5,(x,(43.5+y+BODY_FRONT)/2,-18.75-deflection))
 body=body.fuse(ycyl(3.5,BEARING_GAP,x,y+2.5,free_z-deflection))
 body=body.cut(ycyl(2.6,20,x,y+2.4,free_z-deflection))
 # The bearing-facing foot uses a smaller circular transition to leave the roller clear.
 f=y+BODY_FRONT;z=-27+SPRING_THICKNESS-deflection;r=FRONT_BLEND_RADIUS
 front_round=(cq.Workplane('YZ',origin=(x-5,0,0)).moveTo(f-r,z).lineTo(f,z).lineTo(f,z+r)
  .threePointArc((f-r+r/math.sqrt(2),z+r-r/math.sqrt(2)),(f-r,z)).close().extrude(10).val())
 return leaf.fuse(body,front_round).clean()

def chassis(deflections):
 v=frame
 for p,d in zip(BOTTOM,deflections):v=v.fuse(spring_seat(p,d))
 return v.clean()
