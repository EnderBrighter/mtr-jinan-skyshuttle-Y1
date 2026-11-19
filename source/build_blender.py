"""Build the editable Blender project and render the vehicle, cabin and guideway."""

import sys
from math import pi, sin, cos
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from geometry import (BAND_Y, BAND_Z, BOGIES, DOOR_Z, END, FLOOR, GANGWAY_Y, GANGWAY_Z_OFFSET,
                      LCD_LOWER, LCD_UPPER, LCD_WIDTH, PALETTE, PITCH, TV_HALF, TV_ROWS,
                      RAIL_HALF_LENGTH, RAIL_PITCH, TREAD_EDGES, Mesh, accent, build_body, build_bogie,
                      build_rail, build_wave_markings, door_boxes)

ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'


def collection(name):
    group=bpy.data.collections.new(name)
    scene.collection.children.link(group)
    return group


def linear(c):
    return c/12.92 if c < .04045 else ((c+.055)/1.055)**2.4


def material(name, hex_color, roughness=.55, metal=0, emission=0):
    rgba=[int(hex_color[i:i+2],16)/255 for i in range(1,len(hex_color),2)]
    alpha=rgba[3] if len(rgba)>3 else 1
    rgb=tuple(linear(c) for c in rgba[:3])
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,alpha)
    m.use_nodes=True
    bsdf=m.node_tree.nodes.get('Principled BSDF')
    for setting,value in [('Base Color',(*rgb,1)),('Alpha',alpha),('Roughness',roughness),
                          ('Metallic',metal),('Emission',(*rgb,1)),('Emission Strength',emission)]:
        bsdf.inputs[setting].default_value=value
    if alpha<1:
        m.blend_method='HASHED'
        m.shadow_method='NONE'
        bsdf.inputs['Specular'].default_value=.56
    return m


MATS={n:material(n,c,.29 if n in {'black','mask','roof','white','glass','front_glass'} else .55,
                  .20 if n in {'silver','chrome','beam','beam_lip'} else 0,
                  .72 if n in {'lamp','red'} else 0) for n,c in PALETTE.items()}
atlas=bpy.data.images.load(str(ROOT/'assets/mtr/jinan_y1/textures/atlas.png'))
atlas.pack()
wave_atlas=bpy.data.images.load(str(ROOT/'assets/mtr/jinan_y1/textures/atlas_wave.png'))
wave_atlas.pack();wave_atlas.use_fake_user=True
tiles={'serial':(181,312,343,346),'frontserial':(360,312,521,346),
       'body_band':(10,524,1014,865),
       'accent':(10,244,1014,275),'asphalt':(786,100,1005,219)}
for name in tiles:
    m=material(name,'#e2e7e8',.75 if name=='asphalt' else .40)
    nt=m.node_tree
    texture=nt.nodes.new('ShaderNodeTexImage')
    texture.image=atlas
    nt.links.new(texture.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color'])
    MATS[name]=m
for group,preview in (('lcd_backing','lcd_full.png'),('tv_backing','tv.png')):
    path=ROOT/'preview'/preview
    if path.is_file():
        image=bpy.data.images.load(str(path));image.pack()
        mat=material(group,'#102537',.32)
        nt=mat.node_tree;shader=nt.nodes.get('Principled BSDF')
        texture=nt.nodes.new('ShaderNodeTexImage');texture.image=image
        nt.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
        nt.links.new(texture.outputs['Color'],shader.inputs['Emission'])
        shader.inputs['Emission Strength'].default_value=.55
        MATS[group]=mat
metro_preview=ROOT/'preview/lcd_metro_full.png'
if metro_preview.is_file():
    metro_lcd=bpy.data.images.load(str(metro_preview))
    metro_lcd.pack()
    metro_lcd.use_fake_user=True
else:
    metro_lcd=None
MATS['concrete']=material('Pier concrete','#c2c7c7',.85)
MATS['studio']=material('Studio floor','#5f6e74',.82)


def uv_for(mat, points, custom):
    if mat not in tiles:
        return [(0,0)]*len(points)
    x,y,X,Y=tiles[mat]
    if mat=='body_band':
        custom=[((z-BAND_Z[0])/(BAND_Z[1]-BAND_Z[0]),(BAND_Y[1]-h)/(BAND_Y[1]-BAND_Y[0])) for _,h,z in points]
    if mat=='accent':
        custom=[(accent(z),.5) for _,_,z in points]
    if mat=='asphalt':
        lo,hi=TREAD_EDGES
        custom=[((abs(a)-lo)/(hi-lo),.5+z/(2*RAIL_HALF_LENGTH)) for a,_,z in points]
    return [((x+(X-x)*u)/atlas.size[0],1-(y+(Y-y)*v)/atlas.size[1]) for u,v in custom]


def surface_uv(group,mat,points,custom):
    if group=='lcd_backing':
        return [(.5+(z-DOOR_Z)*(1 if x>0 else -1)/LCD_WIDTH,
                 (y-LCD_LOWER[1])/(LCD_UPPER[1]-LCD_LOWER[1])) for x,y,z in points]
    if group=='tv_backing':
        return [(.5-x/(2*TV_HALF),(y-TV_ROWS[0])/(TV_ROWS[1]-TV_ROWS[0])) for x,y,_ in points]
    return uv_for(mat,points,custom)


def add_mesh(m, target, title, offset=0, turn=False, x_offset=0):
    direction=-1 if turn else 1
    result=[]
    for group,polygons in m.groups.items():
        points,ids,faces=[],{},[]
        mats=list(dict.fromkeys(mat for mat,_,_,_ in polygons))
        for _,face,_,_ in polygons:
            indices=[]
            for point in face:
                key=tuple(round(q,6) for q in point)
                if key not in ids:
                    ids[key]=len(points)
                    x,y,z=point
                    points.append((direction*x+x_offset,-direction*z-offset,y))
                indices.append(ids[key])
            faces.append(indices)
        name=f'{title} | {group}'
        data=bpy.data.meshes.new(name)
        data.from_pydata(points,[],faces)
        data.update()
        for mat in mats:
            data.materials.append(MATS.get(group,MATS[mat]))
        layer=data.uv_layers.new(name='Atlas UV')
        for poly,(mat,pts,uv,smooth) in zip(data.polygons,polygons):
            poly.material_index=mats.index(mat)
            poly.use_smooth=smooth
            for index,coord in zip(poly.loop_indices,surface_uv(group,mat,pts,uv)):
                layer.data[index].uv=coord
        data.use_auto_smooth=True
        obj=bpy.data.objects.new(name,data)
        target.objects.link(obj)
        if all(mat.endswith('glass') for mat in mats):
            obj.hide_render=True
            obj.hide_set(True)
        result.append(obj)
    return result


units=[]
markings=[]
body=build_body()
bogie=build_bogie()
doors=Mesh()
for name,_,_,mat,lo,hi,roll in door_boxes():
    cube=Mesh()
    cube.box(name,mat,lo,hi)
    cx,cy=(lo[0]+hi[0])/2,(lo[1]+hi[1])/2
    for mat,face,uv,smooth in cube.groups[name]:
        points=[(cx+(x-cx)*cos(roll)-(y-cy)*sin(roll),cy+(x-cx)*sin(roll)+(y-cy)*cos(roll),z)
                for x,y,z in face]
        doors.face(name,mat,points,uv=uv,smooth=smooth)
for suffix,offset,turn in (('A',-PITCH/2,False),('B',PITCH/2,True)):
    col=collection('Cab '+suffix+' • shell, cabin & sliding doors')
    exterior=add_mesh(body,col,suffix,offset,turn)
    for obj in exterior:
        if obj.name.endswith('headlights' if turn else 'tail_lights'):
            obj.hide_render=True
            obj.hide_set(True)
    units.extend(exterior)
    units.extend(add_mesh(doors,col,suffix,offset,turn))
    wave_objects=add_mesh(build_wave_markings(),col,suffix,offset,turn)
    for obj in wave_objects:
        obj.hide_render=True
        obj.hide_set(True)
    markings.extend(wave_objects)
    units.extend(wave_objects)
    for index,z in enumerate(BOGIES,1):
        units.extend(add_mesh(bogie,col,f'{suffix} • axle {index}',offset+(-z if turn else z),turn))
    col['car_pitch_m']=PITCH

bellows=Mesh()
gap=PITCH/2-END
for i in range(13):
    z=-gap+.006+i*((2*gap-.031)/12)
    mat='silver' if i%2==0 else 'rubber'
    thickness=.018 if i%2==0 else .024
    for side in (-1,1):
        x,X=sorted((side*.668,side*(1.086 if i%2==0 else 1.023)))
        bellows.box('flexible bellows',mat,(x,.94,z),(X,2.994,z+thickness))
    bellows.box('flexible bellows',mat,(-.83,2.958,z),(.83,3.255,z+thickness))
bellows.box('bridge floor','floor_edge',(-.675,.985,-GANGWAY_Z_OFFSET),
            (.675,GANGWAY_Y+.003125,GANGWAY_Z_OFFSET))
units.extend(add_mesh(bellows,collection('Articulation • straight reference position'),'Centre'))

rail=build_rail(); guideway=collection('Steel guideway • 0.5 m repeat')
rail_segment=add_mesh(rail,guideway,'Guideway mesh')[0]
rail_segment.location.y=-14
copies=rail_segment.modifiers.new('Guideway repeats at 0.5 m','ARRAY')
copies.use_relative_offset=False
copies.use_constant_offset=True
copies.constant_offset_displace=(0,RAIL_PITCH,0)
copies.count=round(28/RAIL_PITCH)+1
rail_segment['running_surface_m']=.255

curve=collection('Steel guideway • 15 m curve reference')
curve.hide_viewport=True
curve.hide_render=True
radius=15
curve_count=round(radius*pi/2)/RAIL_PITCH
curve_step=pi/(2*curve_count)
for i in range(round(curve_count)):
    a,b=i*curve_step,(i+1)*curve_step
    segment=bpy.data.objects.new(f'R15 module {i+1:02d}',rail_segment.data)
    segment.location=(radius*(1-(cos(a)+cos(b))/2),radius*(sin(a)+sin(b))/2,0)
    segment.rotation_euler.z=-(a+b)/2
    curve.objects.link(segment)

studio=collection('Preview lighting & piers')
base=Mesh()
base.box('studio','studio',(-100,-4.22,-100),(100,-4.15,100))
for z in (-10,0,10):
    base.rod('pier','concrete',(0,-4.16,z),(0,-1.24,z),.53,24)
    base.box('pier','concrete',(-.88,-1.385,z-.65),(.88,-1.087,z+.65))
studio_objs=add_mesh(base,studio,'Backdrop')


def aim(obj, point):
    obj.rotation_euler=(Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()


def light(name, loc, power, size, target):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
    obj=bpy.data.objects.new(name,data); obj.location=loc; aim(obj,target); studio.objects.link(obj)


light('Soft daylight',(6,9,10),2900,8,(0,0,1))
light('Overhead fill',(-5,-5,10),1900,9,(0,0,1))
light('Front bounce',(7,-9,3.5),650,7,(0,0,1.5))
for z in (-5,5):
    light('Salon practical',(0,z,2.985),38,1.2,(0,z,FLOOR))
world=bpy.data.worlds.new('Cloudy daylight'); world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.48,.57,.69,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.68
scene.world=world


def camera(name, location, target, focal=52, scale=None):
    data=bpy.data.cameras.new(name)
    data.lens=focal
    data.clip_start=.025
    if scale:
        data.type='ORTHO'; data.ortho_scale=scale
    obj=bpy.data.objects.new(name,data); obj.location=location; aim(obj,target); studio.objects.link(obj)
    return obj


hero=camera('Exterior • three quarter',(11.8,14.9,6.25),(0,.8,1.15),50,21.9)
interior=camera('Cabin • toward the nose',(.035,1.68,1.92),(0,7.80,1.97),21)
railcam=camera('Guideway • section',(4.5,5.2,2.74),(0,0,.09),50,6.0)
curvecam=camera('Guideway • 15 m curve',(.1,15,14),(5.5,10.2,-.25),50,20)
lcdcam=camera('Door header & passenger TV',(-.76,5.38,2.57),(.63,3.73,2.66),21)
tvcam=camera('Passenger TV & articulation',(.07,4.3,2.47),(0,.82,2.86),40)
undercam=camera('Articulation from below',(3.55,.4,.49),(0,0,1.05),44)
scene.camera=hero
scene.render.engine='CYCLES'
scene.cycles.samples=25
scene.cycles.use_denoising=True
scene.render.image_settings.file_format='PNG'
scene.render.resolution_x=1500; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX' if bpy.app.version>=(4,0,0) else 'Filmic'
scene.view_settings.look='Medium High Contrast'
scene.render.film_transparent=False
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.region_3d.view_distance=19
            space.region_3d.view_location=(0,0,1.0)
            space.region_3d.view_rotation=hero.rotation_euler.to_quaternion()
            space.shading.color_type='MATERIAL'

bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/jinan_y1.blend'),compress=True)
for name,view,size in [('exterior',hero,(1500,900)),('wave',hero,(1500,900)),('interior',interior,(1250,810)),
                       ('lcd_installation',lcdcam,(1250,810)),('lcd_metro_installation',lcdcam,(1250,810)),
                       ('tv_installation',tvcam,(1250,810)),
                       ('articulation_underneath',undercam,(1250,810)),
                       ('guideway',railcam,(1140,780)),('guideway_r15',curvecam,(1250,850))]:
    for mat in tiles:
        MATS[mat].node_tree.nodes.get('Image Texture').image=wave_atlas if name=='wave' else atlas
    for obj in markings:
        obj.hide_render=name!='wave'
    if metro_lcd:
        lcd_texture=MATS['lcd_backing'].node_tree.nodes.get('Image Texture')
        if name=='lcd_metro_installation':
            lcd_texture.image=metro_lcd
        elif name=='tv_installation':
            lcd_texture.image=bpy.data.images.get('lcd_full.png')
    if name=='guideway':
        for obj in units:
            obj.hide_render=True
        rail_segment.location.y=-1
        copies.count=5
        studio_objs[1].hide_render=True
    if name=='guideway_r15':
        rail_segment.hide_render=True
        curve.hide_render=False
    scene.camera=view
    scene.render.resolution_x,scene.render.resolution_y=size
    scene.render.filepath=str(ROOT/f'preview/{name}.png')
    bpy.ops.render.render(write_still=True)
    print('Rendered',name,flush=True)
