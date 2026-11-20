"""Original SkyShuttle meshes. X across, Y up, Z along the track, in metres."""

from collections import defaultdict
from math import atan, cos, pi, sin, sqrt


PITCH = 8.8
END = 3.91
NOSE = -2.40
FLOOR = 1.03
FLOOR_UNDERSIDE = .955
CEILING = 3.02
LINER_INSET = .068
GANGWAY_Y = FLOOR + .024
GANGWAY_Z_OFFSET = PITCH/2 - END + .05
TREAD = 0.255
DOOR_Z = .41
DOOR_HALF = .65
DOOR_TOP = FLOOR + 1.85
DOOR_JAMB_CLEARANCE = .004
DOOR_CENTER_CLEARANCE = .0015
LCD_WIDTH = 1.48
LCD_LOWER = (1.023, 2.888)
LCD_UPPER = (.827, 3.002)
LCD_OFFSET = .006
TV_HALF = .227
TV_ROWS = (2.777, 2.985)
TV_Z = 3.614
TV_OFFSET = .006
BAND_Z = (-4.40, END)
BAND_Y = (1.505, 2.95)
BOGIES = (-1.69, 2.51)
WHEEL_HALF_GAUGE = .690
BEAM_HALF_WIDTH = .850
GUIDE_FACE = .519
GUIDE_ROLLER = .112
TREAD_EDGES = (.427, .832)
RAIL_PITCH = .50
RAIL_HALF_LENGTH = .325
PALETTE = {
    'white': '#edf1f0', 'lower': '#dbe3e5', 'roof': '#f5f8f7',
    'black': '#18232c', 'mask': '#24323d', 'rubber': '#242932',
    'gap': '#11181d', 'line': '#63727a', 'silver': '#a7b5bd',
    'chrome': '#d0dee1', 'tire': '#22262b', 'tread': '#30363d',
    'glass': '#31536394', 'front_glass': '#34596a83', 'inside': '#e1e2d9',
    'ceiling': '#f1eee5', 'floor': '#9da29e', 'floor_edge': '#686f6b',
    'seat': '#d5d9d4', 'seat_edge': '#bec6c2', 'priority': '#e5bf38',
    'lamp': '#e4f7ff', 'red': '#ff4149', 'amber': '#e9b750',
    'screen': '#152a32', 'beam': '#9dadb5', 'beam_dark': '#7a8a93',
    'beam_lip': '#c4cdd0', 'asphalt': '#4a5054', 'asphalt_edge': '#565f64',
    'guide': '#6c767d', 'bolt': '#5b6469', 'warning': '#f4c530',
}
ACCENT_STOPS = [(0, (242, 201, 53)), (.24, (236, 198, 55)),
                (.48, (134, 212, 47)), (.64, (40, 188, 106)),
                (.79, (62, 150, 201)), (.90, (111, 101, 208)), (1, (147, 100, 197))]


def interp(samples, x):
    for (a, va), (b, vb) in zip(samples, samples[1:]):
        if x <= b:
            t = max(0, (x - a) / (b - a))
            return va + (vb - va) * t
    return samples[-1][1]


def color_at(t):
    return tuple(round(interp([(p, rgb[i]) for p, rgb in ACCENT_STOPS], t)) for i in range(3))


def accent(z):
    return max(0, min(1, (z - NOSE) / (END - NOSE)))


def wave_profile(t):
    anchors=[(0,1.58),(.15,1.72),(.36,2.91),(.58,2.02),(.77,2.67),(1,2.93)]
    for (a,h),(b,H) in zip(anchors,anchors[1:]):
        if t<=b:
            centre=h+(H-h)*(.5-.5*cos(pi*(t-a)/(b-a)))
            break
    half=interp([(0,.080),(.36,.141),(.58,.153),(1,.115)],t)/2
    return centre,half


def normal(a, b, c):
    u, v = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    length = sqrt(sum(k * k for k in n))
    return tuple(k / length for k in n) if length > 1e-10 else None


class Mesh:
    def __init__(self):
        self.groups = defaultdict(list)

    def face(self, group, material, points, outward=None, uv=None, smooth=False):
        points = list(points)
        n = normal(*points[:3])
        if n is None:
            raise ValueError((group, material, points))
        if outward and sum(a*b for a, b in zip(n, outward)) < 0:
            points.reverse()
            if uv:
                uv = list(reversed(uv))
        self.groups[group].append((material, points, uv, smooth))

    def box(self, group, material, lo, hi, omitted=()):
        x, y, z = lo
        X, Y, Z = hi
        a,b,c,d,e,f,g,h = [(x,y,z), (X,y,z), (X,Y,z), (x,Y,z), (x,y,Z), (X,y,Z), (X,Y,Z), (x,Y,Z)]
        for name, quad in zip(('front','rear','left','right','top','bottom'),
                              ((b,a,d,c),(e,f,g,h),(a,e,h,d),(f,b,c,g),(d,h,g,c),(a,b,f,e))):
            if name not in omitted:
                self.face(group, material, quad)

    def rod(self, group, material, start, end, r, n=10):
        delta = tuple(b-a for a,b in zip(start,end))
        d = tuple(q/sqrt(sum(x*x for x in delta)) for q in delta)
        u = normal((0,0,0), d, (0,0,1) if abs(d[2]) < .9 else (0,1,0))
        v = normal((0,0,0), d, u)
        rings = [[tuple(p[i]+r*(u[i]*cos(2*pi*k/n)+v[i]*sin(2*pi*k/n)) for i in range(3))
                  for k in range(n)] for p in (start,end)]
        for k in range(n):
            j = (k+1)%n
            self.face(group, material, [rings[0][k],rings[0][j],rings[1][j],rings[1][k]], smooth=True)
        self.face(group, material, list(reversed(rings[0])))
        self.face(group, material, rings[1])


HEIGHTS = [.62,.68,.78,.94,1.05,1.29,1.40,1.46,1.505,1.58,1.76,1.91,2.08,
           2.26,2.48,2.68,2.84,2.93,3.01,3.08,3.15,3.22,3.27,3.31,3.33]
WIDTHS = [ .61,.79,.97,1.095,1.16,1.192,1.20,1.20,1.20,1.20,1.193,1.187,1.181,
           1.173,1.155,1.140,1.121,1.102,1.071,1.017,.947,.841,.702,.506,.002]
DEPTHS = [.43,.70,1.04,1.48,1.67,1.87,1.965,1.99,1.99,1.979,1.91,1.84,1.71,
          1.56,1.34,1.09,.88,.75,.65,.56,.48,.42,.38,.35,.33]


def width(y):
    return interp(list(zip(HEIGHTS, WIDTHS)), y)


def door_name(side,leaf):
    return f'door_{"l" if side<0 else "r"}_{"front" if leaf<0 else "rear"}'


def door_span(leaf):
    return sorted((DOOR_Z+leaf*DOOR_CENTER_CLEARANCE,DOOR_Z+leaf*(DOOR_HALF-DOOR_JAMB_CLEARANCE)))


def build_wave_markings(native_door_sizes=False):
    """Exterior solid print on the clear apertures, with no transparent surface."""
    m=Mesh()
    for side in (-1,1):
        spans=[('wave_window',1.59,3.87,.003)]
        for leaf in (-1,1):
            a,b=door_span(leaf)
            if native_door_sizes:
                # Blockbench cuboids are anchored at b and MTR rounds their length to pixels.
                a=max(a,b-round((b-a)*16)/16)
            spans.append(('wave_'+door_name(side,leaf),a,b,.009))
        for name,a,b,offset in spans:
            points=[]
            for i in range(65):
                z=a+(b-a)*i/64
                y,half=wave_profile((z-BAND_Z[0])/(BAND_Z[1]-BAND_Z[0]))
                # Sample slightly inside the matching printed stroke on the atlas.
                lower,upper=y-half+.004,y+half-.004
                points.append(((side*(width(lower)+offset),lower,z),(side*(width(upper)+offset),upper,z)))
            for (p,q),(r,s) in zip(points,points[1:]):
                m.face(name,'body_band',[p,r,s,q],(side,0,0),smooth=True)
    return m


def nose(t, y, lift=0):
    depth = interp(list(zip(HEIGHTS, DEPTHS)), y)
    return ((width(y)+lift)*cos(t), y, NOSE-(depth+lift)*sin(t))


def skin(y):
    if y < .94:
        return 'lower' if y > .77 else 'black'
    if y < 1.46:
        return 'white'
    if y < 1.505:
        return 'accent'
    if y < 3.08:
        return 'mask' if y > 2.95 else 'body_band'
    return 'roof'


def nose_patch(m, group, mat, t0, t1, y0, y1, offset=0, divisions=6):
    rows = sorted({y0, y1, *(y for y in HEIGHTS if y0 < y < y1)})
    ts = [t0+(t1-t0)*i/divisions for i in range(divisions+1)]
    for a,b in zip(ts, ts[1:]):
        for y,Y in zip(rows, rows[1:]):
            t = (a+b)/2
            m.face(group,mat,[nose(a,y,offset),nose(b,y,offset),nose(b,Y,offset),nose(a,Y,offset)],
                   (cos(t),0,-sin(t)), smooth=True)


LOWER_SHELL_TOP=.94


def add_lower_shell(mesh,angles,side_edges):
    """Continuous curved lower shell, with the livery boundary on its surface."""
    floor=TREAD+.030
    # The photographed white chin turns upward into the narrow dark side area.
    stations=[(NOSE,.38,.57),(-2.10,.32,.65),(-1.75,floor,.79),
              (-1.35,floor,.86),(-.80,floor,.86),(.50,floor,.86),
              (3.22,floor,.86),(3.60,.33,.85),(END,.40,.84)]
    heights=[(z,y) for z,y,_ in stations]
    colours=[(z,y) for z,_,y in stations]
    def station_value(values,z):
        for (start,a),(end,b) in zip(values,values[1:]):
            if z<=end:
                blend=.5-.5*cos(pi*max(0,(z-start)/(end-start)))
                return a+(b-a)*blend
        return values[-1][1]
    side_edges=sorted(set(side_edges)|{z for z,_,_ in stations})
    # Resample the length so the end transitions share the smooth cross-section.
    edges=sorted(set(side_edges)|{a+(b-a)*i/4 for a,b in zip(side_edges,side_edges[1:]) for i in range(1,4)})
    outline=[(0,z) for z in reversed(edges[1:])]
    outline.extend((t,NOSE) for t in angles)
    outline.extend((pi,z) for z in edges[1:])
    sections=[]
    for angle,z in outline:
        front=sin(angle) if z==NOSE else 0
        bottom=station_value(heights,z)+.225*front**1.5
        seam=station_value(colours,z)+.080*front**1.5
        topx=width(LOWER_SHELL_TOP)
        depth_top=interp(list(zip(HEIGHTS,DEPTHS)),LOWER_SHELL_TOP)
        ring=[]
        rows=[(1-t)*LOWER_SHELL_TOP+t*seam for t in (0,.25,.50,.75,1)]
        rows += [(1-t)*seam+t*bottom for t in (.25,.5,.75,1)]
        for y in rows:
            f=(LOWER_SHELL_TOP-y)/(LOWER_SHELL_TOP-bottom)
            # Elliptical undercut rounds inward toward the wheel contact level.
            x=topx-.15*f-.103*(1-sqrt(max(0,1-f*f)))
            depth=.27+(depth_top-.27)*(1-f)**.72
            ring.append((x*cos(angle),y,z-depth*front))
        x,y,zz=ring[-1]
        ring.append((x-.045*cos(angle),y+.012,zz+.045*front))
        sections.append(ring)
    for (angle,_),first,last in zip(outline,sections,sections[1:]):
        for i in range(len(first)-1):
            colour='white' if i<4 else 'black'
            mesh.face('shell',colour,[first[i],last[i],last[i+1],first[i+1]],
                      (cos(angle),0,-sin(angle)) if i<8 else (0,-1,0),smooth=True)
    for i in range(len(sections[0])-1):
        mesh.face('shell','black',[sections[-1][i],sections[0][i],sections[0][i+1],sections[-1][i+1]],(0,0,1))


def build_body():
    m = Mesh()
    # Conforming rings give the swept observation windows a continuous edge.
    def ring(y):
        triangle_outer=interp([(1.74,.48),(1.84,.13),(1.96,.14),(2.20,.16),(2.54,.21)],y)
        triangle_inner=interp([(1.74,.51),(1.84,.53),(1.96,.48),(2.20,.38),(2.41,.28),(2.54,.24)],y)
        screen=interp([(1.98,.98),(2.09,.84),(2.20,.753),(2.59,.725),(2.79,.71),(2.89,.76),(2.97,.90)],y)
        return [0,triangle_outer-.029,triangle_outer,triangle_inner,triangle_inner+.030,
                screen-.047,screen,pi/2]

    def ring_angles(y):
        breaks=ring(y)
        half=[breaks[i]+(breaks[i+1]-breaks[i])*k/n
              for i,n in enumerate(divisions) for k in range(n)]
        return [*half,pi/2,*(pi-t for t in reversed(half))]

    panel_rows=sorted(set(HEIGHTS+[FLOOR,1.74,1.84,1.96,1.98,2.09,2.20,2.41,2.54,2.59,2.79,2.89,2.97,CEILING]))
    divisions=(8,2,7,2,7,2,16)
    window_edges={}
    for y,Y in zip(panel_rows,panel_rows[1:]):
        if y<LOWER_SHELL_TOP:
            continue
        h = (y+Y)/2
        r,R=ring(y),ring(Y)
        for index,n in enumerate(divisions):
            mat = skin(h)
            if 1.74<h<2.54 and index in (1,2,3):
                mat='glass' if index==2 and 1.84<h<2.54 else 'gap'
            if 1.98<h<2.97 and index in (5,6):
                mat='front_glass' if index==6 and 2.09<h<2.89 else 'gap'
            group='glazing' if mat.endswith('glass') else 'shell'
            for step in range(n):
                a,b=[r[index]+(r[index+1]-r[index])*k/n for k in (step,step+1)]
                A,B=[R[index]+(R[index+1]-R[index])*k/n for k in (step,step+1)]
                for mirror in (False,True):
                    t=(a+b+A+B)/4
                    ring_points=[(pi-q if mirror else q,v) for q,v in ((a,y),(b,y),(B,Y),(A,Y))]
                    points=[nose(q,v) for q,v in ring_points]
                    outward=((-1 if mirror else 1)*cos(t),0,-sin(t))
                    m.face(group,mat,points,outward,smooth=True)
                    if FLOOR <= y and Y <= CEILING:
                        lining=[nose(q,v,-LINER_INSET) for q,v in ring_points]
                        inner=(-outward[0],0,-outward[2])
                        if group=='glazing':
                            m.face('front_glazing_inside',mat,lining,inner,smooth=True)
                            if sum(i*j for i,j in zip(normal(*points[:3]),outward))<0:
                                ring_points.reverse()
                            for p,q in zip(ring_points,ring_points[1:]+ring_points[:1]):
                                edge=tuple(sorted((tuple(round(v,10) for v in p),tuple(round(v,10) for v in q))))
                                if edge in window_edges:
                                    del window_edges[edge]
                                else:
                                    window_edges[edge]=(p,q)
                        else:
                            lining_mat='rubber' if mat=='gap' else 'inside'
                            m.face('salon',lining_mat,lining,inner,smooth=True)
    for p,q in window_edges.values():
        # Opaque gaskets close the rim between the outer glass and the room-side pane.
        m.face('salon','rubber',[nose(*p),nose(*q),nose(*q,-LINER_INSET),nose(*p,-LINER_INSET)])

    for y,mat,sign in ((FLOOR,'floor',1),(CEILING,'ceiling',-1)):
        angles=ring_angles(y)
        for a,b in zip(angles,angles[1:]):
            m.face('salon',mat,[(0,y,NOSE),nose(a,y,-LINER_INSET),nose(b,y,-LINER_INSET)],(0,sign,0))
    angles=[i*pi/88 for i in range(89)]
    for a,b in zip(angles,angles[1:]):
        for y,mat,sign in ((HEIGHTS[-1],'roof',1),):
            m.face('shell',mat,[(0,y,NOSE),nose(a,y),nose(b,y)],(0,sign,0))
    m.box('shell','roof',(-.002,3.328,NOSE),(.002,3.33,END))
    # Real door and window openings are cut out of both the shell and its lining.
    a,b = DOOR_Z-DOOR_HALF, DOOR_Z+DOOR_HALF
    w0,w1 = 1.68,3.80
    ys = sorted(set(panel_rows+[FLOOR,DOOR_TOP,1.72,1.80,2.64,2.73,2.44,2.49]))
    zs = [NOSE,-1.65,-.77,a,b,1.59,w0,w1,3.87,END]
    add_lower_shell(m,ring_angles(LOWER_SHELL_TOP),zs)
    for side in (-1,1):
        for y,Y in zip(ys,ys[1:]):
            if y<LOWER_SHELL_TOP:
                continue
            h = (y+Y)/2
            for z,Z in zip(zs,zs[1:]):
                if z == a and FLOOR<=h<=DOOR_TOP:
                    continue
                mat = skin(h)
                g = 'shell'
                if 1.72<h<2.73 and 1.59<=z and Z<=3.87:
                    mat = 'gap'
                    if z>=w0 and Z<=w1 and 1.80<h<2.64 and not 2.44<h<2.49:
                        mat, g = 'glass','glazing'
                q = [(side*width(y),y,z),(side*width(y),y,Z),(side*width(Y),Y,Z),(side*width(Y),Y,z)]
                m.face(g,mat,q,(side,0,0),smooth=True)
                if FLOOR <= y and Y <= CEILING and g != 'glazing':
                    mat = 'gap' if mat=='gap' else 'inside'
                    q = [(x-side*LINER_INSET,yy,zz) for x,yy,zz in q]
                    m.face('salon',mat,q,(-side,0,0),smooth=True)
        for z,d in ((a,1),(b,-1)):
            for y,Y in zip(ys,ys[1:]):
                if y>=FLOOR and Y<=DOOR_TOP:
                    x,X = side*width(y),side*width(Y)
                    m.face('shell','rubber',[(x,y,z),(X,Y,z),(X-side*.082,Y,z),(x-side*.082,y,z)],(0,0,d))
        for y,mat in ((FLOOR,'chrome'),(DOOR_TOP,'rubber')):
            x = side*width(y)
            inner = x-side*(LINER_INSET if y==FLOOR else .09)
            m.face('shell',mat,[(x,y,a),(x,y,b),(inner,y,b),(inner,y,a)],(0,1 if y==FLOOR else -1,0))
        # The inboard weather strip covers the narrow top seam of the shut leaves.
        x0,x1=sorted((side*(width(DOOR_TOP)-.108),side*(width(DOOR_TOP)-.091)))
        m.box('salon','rubber',(x0,DOOR_TOP-.014,a-.005),(x1,DOOR_TOP+.006,b+.005))
        # Flush service lines, status lenses and livery plates.
        for z in (-1.60,1.55,3.86):
            for y,Y in ((1.08,1.40),(1.59,2.94)):
                q=[(side*(width(yy)+.0015),yy,zz) for yy,zz in ((y,z),(y,z+.008),(Y,z+.008),(Y,z))]
                m.face('shell','line' if y<1.4 else 'gap',q,(side,0,0))
        for z in (a-.10,b+.10):
            x=side*1.201
            m.box('shell','red',(x-.008,1.455,z-.025),(x+.008,1.533,z+.025))
        z,L,H,y=2.58,.56,.11,1.266
        q=[(side*(width(yy)+.005),yy,zz) for yy,zz in ((y-H/2,z-L/2),(y-H/2,z+L/2),(y+H/2,z+L/2),(y+H/2,z-L/2))]
        uv=[(1,1),(0,1),(0,0),(1,0)] if side==1 else [(0,1),(1,1),(1,0),(0,0)]
        m.face('shell','serial',q,(side,0,0),uv=uv)

    # Curved front lamps, recessed nose cover and forward-facing identification.
    for t0,t1 in ((1.01,1.44),(pi-1.44,pi-1.01)):
        nose_patch(m,'shell','gap',t0-.017,t1+.017,1.56,1.87,.007)
        for y in (1.64,1.752):
            nose_patch(m,'shell','chrome',t0,t1,y,y+.055,.013)
            nose_patch(m,'headlights','lamp',t0+.018,t1-.018,y+.012,y+.041,.018)
        nose_patch(m,'tail_lights','red',t0+.08,t1-.04,1.655,1.687,.024)
    nose_patch(m,'shell','gap',1.34,1.80,.83,.96,.016)
    nose_patch(m,'shell','mask',1.39,1.75,.85,.93,.021)
    q=[nose(1.70,1.535,.012),nose(1.44,1.535,.012),nose(1.44,1.628,.012),nose(1.70,1.628,.012)]
    m.face('shell','frontserial',q,(0,0,-1),uv=[(1,1),(0,1),(0,0),(1,0)])
    m.rod('shell','rubber',nose(1.55,2.12,.021),nose(1.38,2.62,.025),.009,8)
    m.rod('shell','gap',nose(1.30,2.53,.027),nose(1.45,2.72,.027),.011,8)
    m.box('shell','black',(-.40,3.235,-2.91),(.40,3.326,-2.30))
    # The center belly closes the shell without flats extending past the wheels.
    m.box('shell','black',(-.60,.612,NOSE),(.60,.645,END))
    # Recess the end skirt so its end face never overlays the end of the floor slab.
    m.box('shell','rubber',(-.86,.76,END-.125),(.86,FLOOR_UNDERSIDE+.002,END-.016),('up',))
    m.box('salon','inside',(-1.11,2.91,END-.125),(1.11,3.11,END),('down',))
    for side in (-1,1):
        x0,x1=sorted((side*.726,side*1.11))
        m.box('salon','inside',(x0,FLOOR+.004,END-.125),(x1,2.91,END),('up',))
        x0,x1=sorted((side*.699,side*.726))
        m.box('salon','rubber',(x0,FLOOR+.004,END-.143),(x1,2.903,END+.015))
    m.face('salon','inside',[(-.726,2.91,END-.125),(.726,2.91,END-.125),
                            (.726,2.91,END),(-.726,2.91,END)],(0,-1,0))

    # Air conditioners, covers and vent grilles sit inside the roof's broad white crown.
    for z in (-1.44,):
        m.box('shell','white',(-.75,3.23,z-.59),(.75,3.343,z+.59))
        for x in (-.51,-.17,.17,.51):
            m.rod('shell','gap',(x,3.342,z+.25),(x,3.356,z+.25),.115,24)
            for k in range(-3,4):
                dz=k*.027
                w=sqrt(.11**2-dz**2)
                m.rod('shell','silver',(x-w,3.362,z+.25+dz),(x+w,3.362,z+.25+dz),.005,6)
            for i in range(5):
                dz=z-.44+i*.072
                m.box('shell','mask',(x-.13,3.343,dz),(x+.13,3.350,dz+.045))
    for z in (-.38,.56,1.49,3.28):
        for s in (-1,1):
            m.rod('shell','line',(s*.012,3.329,z),(s*.54,3.306,z),.004,5)
    for x in (-.34,.34):
        m.box('shell','mask',(x-.11,3.258,END-.47),(x+.11,3.353,END-.13))
        for i in range(4):
            z=END-.42+i*.064
            m.rod('shell','silver',(x-.093,3.358,z),(x+.093,3.358,z),.005,6)
    build_interior(m)
    return m


def build_interior(m):
    floor_half=width(FLOOR)-LINER_INSET
    m.box('salon','floor',(-floor_half,FLOOR_UNDERSIDE,NOSE),(floor_half,FLOOR,END),('front',))
    m.box('salon','inside',(-.61,FLOOR,-3.63),(.61,1.36,-3.43))
    m.box('salon','inside',(-.87,1.36,-3.58),(.87,1.43,-3.29))
    m.box('salon','screen',(-.20,1.432,-3.56),(.20,1.439,-3.42))
    m.box('salon','ceiling',(-.69,CEILING,NOSE),(.69,3.075,END),('front','left','right'))
    for side in (-1,1):
        edge=side*(width(CEILING)-LINER_INSET)
        x=side*.69
        m.face('salon','ceiling',[(x,CEILING,NOSE),(edge,CEILING,NOSE),
                                 (edge,CEILING,END),(x,CEILING,END)],(0,-1,0))
        lo,hi=sorted((side*.65,side*.98))
        seat_clearance=DOOR_HALF+.12
        for z,Z in ((-2.46,DOOR_Z-seat_clearance),(DOOR_Z+seat_clearance,END-.045)):
            # Sculpted continuous seat pan and back, with a small priority zone at the front.
            for s,t,mat in ((z,z+.51,'priority'),(z+.512,Z,'seat')):
                section=[(.63,1.435),(.644,1.50),(.705,1.536),(.929,1.542),(1.008,1.63),
                         (1.016,1.88),(1.053,1.927),(1.084,1.90),(1.090,1.45),(.98,1.40),(.68,1.408)]
                for u,v in zip(section,section[1:]+section[:1]):
                    x,y=u; X,Y=v
                    m.face('salon',mat,[(side*x,y,s),(side*x,y,t),(side*X,Y,t),(side*X,Y,s)],
                           outward=(-side*(Y-y),X-x,0),smooth=True)
                for end,sgn in ((s,-1),(t,1)):
                    for u,v in zip(section,section[1:]+section[:1]):
                        m.face('salon','seat_edge',[(side*.97,1.487,end),(side*u[0],u[1],end),
                                                  (side*v[0],v[1],end)],(0,0,sgn))
            m.box('salon','inside',(lo,FLOOR,z+.045),(hi,1.405,Z-.045))
        x,X=sorted((side*.47,side*.55))
        m.box('lights','lamp',(x,3.006,-2.39),(X,3.021,END-.12))
        for start,end,tie in ((-2.47,DOOR_Z-.88,DOOR_Z-.91),(DOOR_Z+.88,END-.12,DOOR_Z+.91)):
            m.rod('salon','chrome',(side*.65,2.79,start),(side*.65,2.79,end),.014)
            m.rod('salon','chrome',(side*.65,2.79,tie),(side*.65,CEILING,tie),.011)
        for z in (-2.14,-1.61,-1.08,1.58,2.08,2.58,3.08,3.58):
            x=side*.65
            m.rod('salon','rubber',(x,2.8,z),(x,2.64,z),.014,8)
            for d in (-1,1):
                m.rod('salon','chrome',(x,2.64,z+d*.022),(x,2.512,z+d*.072),.009,8)
            m.rod('salon','chrome',(x,2.512,z-.072),(x,2.512,z+.072),.012,8)
        for z in (DOOR_Z-DOOR_HALF-.13,DOOR_Z+DOOR_HALF+.13):
            m.rod('salon','chrome',(side*.64,FLOOR,z),(side*.63,2.84,z),.021,12)
            m.rod('salon','chrome',(side*.64,1.78,z),(side*1.06,1.93,z),.014,10)
        for i in range(23):
            z=-2.35+i*.272
            v0,v1=sorted((side*.708,side*.942))
            m.box('salon','screen',(v0,3.014,z),(v1,3.022,z+.015))
        build_lcd_header(m,side)
    for z in (-2.36,-.63,1.39,3.79):
        m.rod('salon','chrome',(-.94,2.795,z),(.94,2.795,z),.018)
    m.rod('salon','chrome',(0,FLOOR,-2.31),(0,3.03,-2.31),.019,12)
    # Widescreen casing and two ceiling mounts, proportioned to the real TV.
    m.box('salon','rubber',(-.255,2.754,TV_Z+.002),(.255,3.007,TV_Z+.077))
    m.box('salon','mask',(-.236,2.767,TV_Z+.001),(.236,2.995,TV_Z+.008))
    low,high=TV_ROWS
    m.face('tv_backing','screen',[(-TV_HALF,low,TV_Z),(TV_HALF,low,TV_Z),
                                 (TV_HALF,high,TV_Z),(-TV_HALF,high,TV_Z)],(0,0,-1))
    for x in (-.192,.192):
        m.box('salon','rubber',(x-.024,2.996,TV_Z+.028),(x+.024,3.029,TV_Z+.064))


def build_lcd_header(m, side):
    low_x,low_y=LCD_LOWER
    up_x,up_y=LCD_UPPER
    half=LCD_WIDTH/2
    bezel=half+.08
    edges=[-bezel,-half-.008,-half,half,half+.008,bezel]
    # The door header is an opaque wedge tied to the existing jamb and ceiling.
    rows=[(low_x+.012,DOOR_TOP),(low_x+.008,low_y-.005),(low_x,low_y),
          (up_x,up_y),(up_x-.008,up_y+.005),(up_x-.025,CEILING)]
    for j,((x,y),(X,Y)) in enumerate(zip(rows,rows[1:])):
        for i,(z,Z) in enumerate(zip(edges,edges[1:])):
            group,mat='salon','inside'
            if i==j==2:
                group,mat='lcd_backing','screen'
            elif 1<=i<=3 and 1<=j<=3:
                mat='rubber'
            m.face(group,mat,[(side*x,y,DOOR_Z+z),(side*x,y,DOOR_Z+Z),
                (side*X,Y,DOOR_Z+Z),(side*X,Y,DOOR_Z+z)],(-side,-1,0))
    for z in (edges[0],edges[-1]):
        m.face('salon','inside',[(side*rows[0][0],DOOR_TOP,DOOR_Z+z),
               (side*(width(DOOR_TOP)-.044),DOOR_TOP,DOOR_Z+z),
               (side*(width(CEILING)-.061),CEILING,DOOR_Z+z),
               (side*rows[-1][0],CEILING,DOOR_Z+z)],(0,0,z))
    for z in (-.66,.66):
        m.rod('salon','amber' if z>0 else 'red',(side*1.045,DOOR_TOP-.011,DOOR_Z+z),
              (side*1.045,DOOR_TOP-.001,DOOR_Z+z),.012,12)


def door_boxes():
    """Door frame, glazing and two-tone skin in MTR-compatible cuboids."""
    for side in (-1,1):
        for leaf in (-1,1):
            z0,z1=door_span(leaf)
            name=door_name(side,leaf)
            low,high=1.74,2.72
            sill,head=FLOOR+.004,DOOR_TOP-.003
            a,b=z0+.081,z1-.081
            for y,Y,z,Z,mat in [(sill,1.46,z0,z1,'white'),(1.46,1.505,z0,z1,'accent'),
                                (1.505,low,z0,z1,'black'),(high,head,z0,z1,'black'),
                                (low,high,z0,a,'black'),(low,high,b,z1,'black'),
                                (low,high,a,b,'glass')]:
                yield door_box(name+('_glass' if mat=='glass' else ''),side,leaf,mat,y,Y,z,Z,
                               (-.041,-.030) if mat=='glass' else (-.066,.002))
            for y,Y,z,Z in [(sill,low,z0+.006,z1-.006),(high,head,z0+.006,z1-.006),
                             (low,high,z0+.006,a-.008),(low,high,b+.008,z1-.006)]:
                yield door_box(name,side,leaf,'inside',y,Y,z,Z,(-.077,-.064))
            seam=sorted((DOOR_Z+leaf*DOOR_CENTER_CLEARANCE,DOOR_Z+leaf*.013))
            yield door_box(name,side,leaf,'rubber',sill,head,*seam,(-.087,-.076))


def door_box(name,side,leaf,mat,y,Y,z,Z,depth):
    centre=(width(y)+width(Y))/2
    angle=-atan(side*(width(Y)-width(y))/(Y-y))
    x,X=sorted(side*(centre+d) for d in depth)
    return name,side,leaf,mat,(x,y,z),(X,Y,Z),angle


def build_bogie():
    m=Mesh()
    g='bogie'
    m.box(g,'mask',(-.74,.65,-.31),(.74,.80,.31))
    m.box(g,'black',(-.35,.525,-.28),(.35,.68,.28))
    for side in (-1,1):
        x=side*WHEEL_HALF_GAUGE
        # Rubber load wheels use a shouldered tire and inset multi-bolt alloy hub.
        sections=[(-.132,.242),(-.117,.288),(-.084,.305),(.082,.305),(.121,.285),(.132,.239),(.132,.188)]
        y=TREAD+.305
        for i,((u,r),(v,R)) in enumerate(zip(sections,sections[1:])):
            for j in range(24):
                a,b=j*pi/12,(j+1)*pi/12
                q=[(x+side*d,y+R0*cos(t),R0*sin(t)) for d,R0,t in ((u,r,a),(u,r,b),(v,R,b),(v,R,a))]
                m.face(g,'tread' if i in (1,2,3) else 'tire',q,(side*(r-R),cos((a+b)/2),sin((a+b)/2)),smooth=True)
        outer=x+side*.132
        m.rod(g,'silver',(x,y,0),(outer+side*.005,y,0),.183,24)
        m.rod(g,'mask',(outer+side*.006,y,0),(outer+side*.015,y,0),.125,18)
        m.rod(g,'silver',(outer+side*.017,y,0),(outer+side*.038,y,0),.069,14)
        for i in range(6):
            a=i*pi/3
            m.rod(g,'chrome',(outer+side*.012,y+.104*cos(a),.104*sin(a)),
                  (outer+side*.032,y+.104*cos(a),.104*sin(a)),.013,6)
        for z in (-.38,.38):
            guide_x=side*(GUIDE_FACE-GUIDE_ROLLER)
            m.rod(g,'rubber',(guide_x,.042,z),(guide_x,.153,z),GUIDE_ROLLER,24)
            m.rod(g,'silver',(guide_x,.154,z),(guide_x,.168,z),.068,14)
            m.rod(g,'line',(side*.375,.167,z),(side*.39,.65,z*.51),.031,9)
        m.rod(g,'warning',(side*.55,.65,-.22),(side*.58,.87,-.22),.027,12)
    return m


def triangulate_profile(points):
    """Triangulate a counterclockwise section, retaining its collinear edge vertices."""
    def turn(a,b,c):
        ax,ay=points[a]
        bx,by=points[b]
        cx,cy=points[c]
        return (bx-ax)*(cy-ay)-(by-ay)*(cx-ax)

    remaining=list(range(len(points)))
    while len(remaining)>3:
        for i,b in enumerate(remaining):
            a,c=remaining[i-1],remaining[(i+1)%len(remaining)]
            if turn(a,b,c)<=1e-10:
                continue
            if any(min(turn(a,b,p),turn(b,c,p),turn(c,a,p))>=-1e-10
                   for p in remaining if p not in (a,b,c)):
                continue
            yield a,b,c
            remaining.pop(i)
            break
        else:
            raise ValueError('Cannot triangulate the rail section')
    yield tuple(remaining)


def build_rail():
    m=Mesh()
    def sweep(profile, center, side=1):
        # Recess both tips so successive copies can overlap without coplanar faces.
        cx,cy=center
        rings=[[(side*(cx+(x-cx)*scale),cy+(y-cy)*scale,z) for x,y,_ in profile]
               for z,scale in ((-RAIL_HALF_LENGTH,.993),(0,1),(RAIL_HALF_LENGTH,.993))]
        for near,far in zip(rings,rings[1:]):
            for i,(_,_,mat) in enumerate(profile):
                j=(i+1)%len(profile)
                q=[near[i],near[j],far[j],far[i]]
                m.face('guideway',mat,q if side>0 else reversed(q),smooth=True)
        # The end caps follow the recessed section so they stay inside the overlap.
        for triangle in triangulate_profile([(x,y) for x,y,_ in profile]):
            for ring,direction in ((rings[0],-1),(rings[-1],1)):
                m.face('guideway','beam_dark',[ring[i] for i in triangle],(0,0,direction))

    # One continuous profile per beam joins the running strip, guide face and flanges.
    inner,outer=TREAD_EDGES
    beam=[
        (.415,-1.09,'beam_dark'),(.840,-1.09,'beam_dark'),(.840,-1.027,'beam_dark'),
        (.777,-1.027,'beam'),(.777,.173,'beam_lip'),(BEAM_HALF_WIDTH,.173,'beam_lip'),
        (BEAM_HALF_WIDTH,.219,'asphalt_edge'),(BEAM_HALF_WIDTH,.249,'asphalt_edge'),
        (outer,.249,'asphalt_edge'),(outer,TREAD,'asphalt'),(inner,TREAD,'asphalt_edge'),
        (inner,.219,'beam_lip'),(.415,.219,'beam_lip'),(.415,.173,'beam_lip'),
        (GUIDE_FACE+.003,.173,'beam'),(GUIDE_FACE+.003,.158,'guide'),
        (GUIDE_FACE,.158,'guide'),(GUIDE_FACE,.024,'guide'),(GUIDE_FACE+.003,.024,'beam'),
        (GUIDE_FACE+.003,-1.027,'beam_dark'),(.415,-1.027,'beam_dark'),
    ]
    for side in (-1,1):
        sweep(beam,(.63,-.42),side)
        a,b=sorted((side*.773,side*.820))
        m.box('guideway','beam_lip',(a,-1.025,-.019),(b,.172,.019))
    walkway=[(-.542,-.277,'beam_dark'),(.542,-.277,'beam_dark'),
             (.542,-.239,'guide'),(-.542,-.239,'beam_dark')]
    sweep(walkway,(0,-.258))
    for y,Y in ((-.94,-.90),(-.54,-.50)):
        m.box('guideway','beam_lip',(-.552,y,-.085),(.552,Y,.085))
    m.box('guideway','beam',(-.553,-.899,-.019),(.553,-.538,.019))
    m.box('guideway','beam_dark',(-.449,-.495,-.036),(.449,-.276,.036))
    return m
