"""Build the MTR 4 resource pack from the original editable geometry."""

import base64
import json
import random
import uuid
import zipfile
from collections import defaultdict
from pathlib import Path
from copy import deepcopy
from math import copysign, degrees, sqrt

from PIL import Image, ImageDraw, ImageFont

from geometry import (BAND_Y, BAND_Z, BOGIES, DOOR_HALF, DOOR_Z, END, FLOOR, GANGWAY_Y, GANGWAY_Z_OFFSET,
                      LCD_LOWER, LCD_OFFSET, LCD_UPPER, LCD_WIDTH, PALETTE, PITCH, TV_HALF, TV_OFFSET, TV_ROWS, TV_Z,
                      RAIL_HALF_LENGTH, RAIL_PITCH, TREAD_EDGES, accent, build_body, build_bogie, build_rail,
                      build_wave_markings, color_at, door_boxes, interp, normal, wave_profile)

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/mtr/jinan_y1'
PREFIX = 'mtr:jinan_y1/'
W, H = 1024, 1024
IMAGE = 'textures/atlas.png'
WAVE_IMAGE = 'textures/atlas_wave.png'
TILES = {
    'serial': (181,312,343,346),
    'frontserial': (360,312,521,346), 'accent': (10,244,1014,275),
    'body_band': (10,524,1014,865),
    'asphalt': (786,100,1005,219),
}
SWATCHES = {name: (24+(i%16)*48, 24+(i//16)*52) for i,name in enumerate(PALETTE)}
FACES = ('north','east','south','west','up','down')
VEHICLE_DESCRIPTION = '\n'.join((
    '最高时速：80 km/h',
    '建议加速度：1.0 m/s²',
    '最小转弯半径：50 m',
    '极限转弯半径：15 m',
))


def font(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/msyh' + ('bd' if bold else '') + '.ttc', size)


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def make_textures():
    atlas = Image.new('RGBA', (W,H), '#252d33')
    d = ImageDraw.Draw(atlas)
    for name,(x,y) in SWATCHES.items():
        d.rectangle((x-21,y-21,x+21,y+21),fill=PALETTE[name][:7])
    x,y,X,Y=TILES['accent']
    for u in range(x-3,X+4):
        d.line((u,y-3,u,Y+3),fill=color_at((u-x)/(X-x))+(255,))
    rng=random.Random(101)
    x,y,X,Y=TILES['asphalt']
    for v in range(y-3,Y+4):
        for u in range(x-3,X+4):
            g=74+rng.randint(-4,4)
            atlas.putpixel((u,v),(g,g+5,g+8,255))
    for tile,background,string,size,fg in (
        ('serial','white','Y0115',24,'#283b45'), ('frontserial','black','Y0115',23,'#e5efec'),
    ):
        x,y,X,Y=TILES[tile]
        d.rectangle((x-4,y-4,X+4,Y+4),fill=PALETTE[background])
        d.text(((x+X)//2,(y+Y)//2),string,font=font(size,True),fill=fg,anchor='mm')
    x,y,X,Y=TILES['body_band']
    d.rectangle((x-4,y-4,X+4,Y+4),fill=PALETTE['black'])
    atlas.save(BASE/IMAGE)
    for tile,mat in (('serial','white'),('frontserial','black')):
        a,b,A,B=TILES[tile]
        d.rectangle((a-4,b-4,A+4,B+4),fill=PALETTE[mat])
    for u in range(x-3,X+4):
        t=max(0,min(1,(u-x)/(X-x)))
        centre,half=wave_profile(t)
        color=color_at(interp([(0,0),(.36,.23),(.58,.52),(.78,.83),(1,1)],t))
        v=y+(Y-y)*(BAND_Y[1]-centre)/(BAND_Y[1]-BAND_Y[0])
        half_pixels=(Y-y)*half/(BAND_Y[1]-BAND_Y[0])
        for row in range(max(y-3,int(v-half_pixels)),min(Y+3,int(v+half_pixels)+1)+1):
            d.point((u,row),fill=color+(255,))
    atlas.save(BASE/WAVE_IMAGE)

    gangway=Image.new('RGB',(64,64),'#222b32')
    d=ImageDraw.Draw(gangway)
    for x in range(0,64,8):
        d.rectangle((x,0,x+2,63),fill='#546268')
        d.line((x+3,0,x+3,63),fill='#39454c')
    gangway.save(BASE/'textures/gangway.png')

    icon=Image.new('RGB',(128,128),'#17282f'); d=ImageDraw.Draw(icon)
    d.rounded_rectangle((23,22,106,98),radius=24,fill='#ecf2f4')
    d.rounded_rectangle((24,25,105,80),radius=21,fill='#182631')
    d.line((28,79,100,79),fill='#ecd046',width=3)
    for x in (39,79):
        d.rounded_rectangle((x,65,x+11,68),2,fill='#d6f0f5')
    d.text((65,48),'Y1',font=font(23,True),fill='#d5e6e8',anchor='mm')
    d.rounded_rectangle((15,103,113,112),2,fill='#a6b9c2')
    icon.save(ROOT/'pack.png')


def uvs(mat, points, custom):
    if mat in ('body_band','body_band_flipped'):
        x,y,X,Y=TILES['body_band']
        yaw=-1 if mat=='body_band_flipped' else 1
        return [((x+(X-x)*(yaw*z-BAND_Z[0])/(BAND_Z[1]-BAND_Z[0]))/W,
                 (y+(Y-y)*(BAND_Y[1]-h)/(BAND_Y[1]-BAND_Y[0]))/H) for _,h,z in points]
    if mat == 'accent':
        x,y,X,Y=TILES[mat]
        return [((x+(X-x)*accent(z))/W, ((y+Y)/2)/H) for _,_,z in points]
    if mat == 'asphalt':
        x,y,X,Y=TILES[mat]
        lo,hi=TREAD_EDGES
        return [((x+(X-x)*((abs(a)-lo)/(hi-lo)))/W,
                 (y+(Y-y)*(.5+z/(2*RAIL_HALF_LENGTH)))/H) for a,_,z in points]
    if custom:
        x,y,X,Y=TILES[mat]
        return [((x+(X-x)*u)/W,(y+(Y-y)*v)/H) for u,v in custom]
    x,y=SWATCHES[mat]
    return [(x/W,y/H)]*len(points)


def write_obj(name, mesh, material='yunba.mtl', *, double_sided=False):
    vertices, texture, normals = {}, {}, {}
    records=['# Jinan SkyShuttle Y1 | metres','mtllib '+material]
    def add(key, ids, label):
        point=tuple(round(t,6) for t in key)
        if point not in ids:
            ids[point]=len(ids)+1
            records.append(f'{label} ' + ' '.join(f'{v:.6f}' for v in point))
        return ids[point]

    for group, faces in mesh.groups.items():
        records.extend((f'g {group}','usemtl atlas'))
        adjacent=defaultdict(list)
        for _,points,_,smooth in faces:
            if smooth:
                n=normal(*points[:3])
                for p in points:
                    adjacent[tuple(round(q,5) for q in p)].append(n)
        for mat,points,uv,smooth in faces:
            tex=uvs(mat,points,uv)
            n=normal(*points[:3])
            polygon=[]
            for p,t in zip(points,tex):
                filtered=[a for a in adjacent[tuple(round(q,5) for q in p)]
                          if sum(u*v for u,v in zip(a,n))>.78] if smooth else []
                avg=tuple(sum(a[i] for a in filtered) for i in range(3)) if filtered else n
                norm=sqrt(sum(x*x for x in avg))
                polygon.append(f'{add(p,vertices,"v")}/{add(t,texture,"vt")}/{add(tuple(x/norm for x in avg),normals,"vn")}')
            for i in range(1,len(polygon)-1):
                if normal(points[0],points[i],points[i+1]):
                    triangle=(polygon[0],polygon[i],polygon[i+1])
                    records.append('f '+' '.join(triangle))
                    if double_sided:
                        # Reuse the same UVs and lighting in renderers that draw both windings.
                        records.append('f '+' '.join(reversed(triangle)))
    (BASE/f'models/{name}.obj').write_text('\n'.join(records)+'\n',encoding='ascii')


def uuid_for(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'https://jinan-y1.local/' + name))


def bb_write(name, boxes):
    elements=[]
    groups=defaultdict(list)
    for group,mat,lo,hi,roll in boxes:
        x,y,z=lo
        X,Y,Z=hi
        uid=uuid_for(f'{name}/cube/{len(elements)}')
        u,v=SWATCHES.get(mat,SWATCHES['white'])
        # Each box reserves a uniformly coloured tile for the native box-UV renderer.
        # The accent panel instead samples its part of the continuous waist stripe.
        if mat=='accent':
            a,b,A,B=TILES['accent']
            u=round(a+(A-a)*accent((z+Z)/2))
            v=(b+B)//2
        uv=[u-1,v-1,u+1,v+1]
        u0=round(u-16*((X-x)+(Z-z)))
        v0=round(v-8*((Y-y)+2*(Z-z)))
        elements.append({'uuid':uid,'name':group,'type':'cube','from':[-X*16,y*16,-Z*16],
                         'to':[-x*16,Y*16,-z*16],
                         'origin':[-(x+X)*8,(y+Y)*8,-(z+Z)*8] if roll else [0,0,0],
                         'rotation':[0,0,-degrees(roll)],'box_uv':True,
                         'uv_offset':[max(0,u0),max(0,v0)],
                         'faces':{face:{'uv':uv,'texture':0} for face in FACES}})
        groups[group].append(uid)
    dump(BASE/f'models/{name}.bbmodel',{'meta':{'format_version':'4.9','model_format':'modded_entity','box_uv':False},
        'name':name,'resolution':{'width':W,'height':H},'elements':elements,
        'outliner':[{'name':g,'origin':[0,0,0],'uuid':uuid_for(f'{name}/group/{g}'),'children':ids} for g,ids in groups.items()],
        'textures':[{'id':'0','name':'atlas.png','source':'data:image/png;base64,'+
                     base64.b64encode((BASE/IMAGE).read_bytes()).decode('ascii')}]})


def part(names, position='origin', **fields):
    return {'names':names,'positionDefinitions':[position],**fields}


def properties(name, parts, **fields):
    dump(BASE/f'properties/{name}.json',{'parts':parts,'modelYOffset':0,**fields})


def model(name, props=None, extension='obj'):
    return {'modelResource':PREFIX+f'models/{name}.{extension}', 'textureResource':PREFIX+IMAGE,
            'modelPropertiesResource':PREFIX+f'properties/{props or name}.json',
            'positionDefinitionsResource':PREFIX+'properties/origin.json','flipTextureV':False}


def build_pack():
    for sub in ('models','properties','textures','scripts'):
        (BASE/sub).mkdir(parents=True,exist_ok=True)
    make_textures()
    # Leave the clear panes out of the game render so they cannot occlude water in the depth buffer.
    body=build_body()
    del body.groups['glazing'], body.groups['front_glazing_inside']
    for name, mesh in (('end_car',body),('rubber_bogie',build_bogie())):
        write_obj(name,mesh)
    write_obj('steel_guideway',build_rail(),double_sided=True)
    wave=build_wave_markings(native_door_sizes=True)
    # MTR 4.0.5 applies an animated OBJ's flip at both cache and draw time.
    # Export the A-end yaw here and let both sets of door graphics use origin.
    # The OBJ cache also applies PLUG_SLOW's closed X offset of 0.05 pixels.
    closed_x=.05/16
    for group,faces in tuple(wave.groups.items()):
        if not group.startswith('wave_door_'):
            continue
        wave.groups[group]=[(mat,[(x-copysign(closed_x,x),y,z) for x,y,z in points],uv,smooth)
                            for mat,points,uv,smooth in faces]
        wave.groups[group.replace('wave_', 'wave_flipped_', 1)]=[
            ('body_band_flipped',[(-x,y,-z) for x,y,z in points],uv,smooth)
            for _,points,uv,smooth in wave.groups[group]]
    wave.groups.update(body.groups)
    write_obj('end_car_wave',wave,'yunba_wave.mtl')
    (BASE/'models/yunba.mtl').write_text(f'newmtl atlas\nKd 1 1 1\nd 1\nmap_Kd {PREFIX+IMAGE}\n',encoding='ascii')
    (BASE/'models/yunba_wave.mtl').write_text(f'newmtl atlas\nKd 1 1 1\nd 1\nmap_Kd {PREFIX+WAVE_IMAGE}\n',encoding='ascii')
    dump(BASE/'properties/origin.json',{'positionDefinitions':[{'name':'origin','positions':[{}]},
                                                             {'name':'flipped','positionsFlipped':[{}]}]})
    moving=[box for box in door_boxes() if box[3]!='glass']
    bb_write('doors',[(g,mat,lo,hi,roll) for g,_,_,mat,lo,hi,roll in moving])
    # MTR rounds cuboid sizes to whole Blockbench pixels when it calculates bounds.
    doorway_x=(1.03,1.03+10/16)
    doorway_y=(FLOOR-1/16,FLOOR)
    doorway_half=round((DOOR_HALF-.032)*32)/32
    interactions=[('floor','floor',(-1.067,FLOOR-.062,-3.13),(1.067,FLOOR,END+.008))]
    for side in (-1,1):
        x,X=sorted(side*edge for edge in doorway_x)
        interactions.append((f'doorway_{side}','floor',(x,doorway_y[0],DOOR_Z-doorway_half),
                             (X,doorway_y[1],DOOR_Z+doorway_half)))
    bb_write('interaction',[(*box,0) for box in interactions])
    properties('rubber_bogie',[part(['bogie'],renderStage='EXTERIOR')])

    vehicles=[]
    for reverse in (False,True):
        suffix='rear' if reverse else 'front'
        static='origin' if reverse else 'flipped'
        parts=[part(['shell'],static,renderStage='EXTERIOR'),
               part(['salon','lcd_backing','tv_backing'],static,renderStage='INTERIOR'),
               part(['lights'],static,renderStage='LIGHT'),
               part(['headlights'],static,renderStage='ALWAYS_ON_LIGHT',condition='ON_ROUTE_BACKWARDS' if reverse else 'ON_ROUTE_FORWARDS'),
               part(['tail_lights'],static,renderStage='ALWAYS_ON_LIGHT',condition='ON_ROUTE_FORWARDS' if reverse else 'ON_ROUTE_BACKWARDS')]
        gangway={f'gangway{surface}{face}Resource':PREFIX+'textures/gangway.png'
                 for surface in ('Inner','Outer') for face in ('Side','Top','Bottom')}
        gangway.update(gangwayWidth=1.35,gangwayHeight=2.95-GANGWAY_Y,
                       gangwayYOffset=GANGWAY_Y,gangwayZOffset=GANGWAY_Z_OFFSET)
        properties(f'body_{suffix}',parts,**gangway)
        doors={g:part([g],static,renderStage='INTERIOR',
                      doorAnimationType='PLUG_SLOW',doorXMultiplier=side*1.72,
                      doorZMultiplier=-leaf*16*(DOOR_HALF+.005))
               for g,side,leaf,_,_,_,_ in moving}
        properties(f'doors_{suffix}',list(doors.values()))
        wave_parts=[part(['wave_window'],static,renderStage='EXTERIOR')]
        wave_prefix='wave_' if reverse else 'wave_flipped_'
        yaw=1 if reverse else -1
        for name,p in doors.items():
            wave_parts.append(part([wave_prefix+name],renderStage='EXTERIOR',
                                   doorAnimationType=p['doorAnimationType'],
                                   doorXMultiplier=yaw*p['doorXMultiplier'],
                                   doorZMultiplier=yaw*p['doorZMultiplier']))
        properties(f'body_wave_{suffix}',parts+wave_parts,**gangway)
        # The Blockbench bounds and visible doors both use the car's yaw.
        properties(f'interaction_{suffix}',[part([g],static,type='FLOOR' if g=='floor' else 'DOORWAY')
                                             for g,_,_,_ in interactions])
        bogies=BOGIES if not reverse else tuple(-p for p in reversed(BOGIES))
        vehicles.append({'id':f'jinan_y1_{suffix}','name':'济南云巴1号线 | '+('B端车 ←' if reverse else 'A端车 →'),
            'description':VEHICLE_DESCRIPTION,
            'transportMode':'TRAIN','color':'E7CD44','length':PITCH,'width':2.4,
            'couplingPadding1':0,'couplingPadding2':0,
            'bogie1Position':bogies[0],'bogie2Position':bogies[1],
            'hasGangway1':reverse,'hasGangway2':not reverse,
            'tags':['family:jinan_y1','iso_3166:CN','doors:1','length:8.8m'],
            'models':[model('end_car',f'body_{suffix}'),model('doors',f'doors_{suffix}','bbmodel'),
                      model('interaction',f'interaction_{suffix}','bbmodel')],
            'bogie1Models':[model('rubber_bogie')],'bogie2Models':[model('rubber_bogie')],
            'legacySpeedSoundBaseResource':'mpl_85','legacySpeedSoundCount':48,
            'legacyDoorSoundBaseResource':'mpl_85','legacyDoorCloseSoundTime':1,'scriptId':'jinan_y1_displays'})
    for base_car in list(vehicles):
        variant=deepcopy(base_car)
        variant['id']=variant['id'].replace('jinan_y1_', 'jinan_y1_wave_')
        variant['name']=variant['name'].replace(' | ', '（彩波纹） | ')
        variant['color']='8672BD'
        variant['models'][0]['modelResource']=PREFIX+'models/end_car_wave.obj'
        variant['models'][0]['textureResource']=PREFIX+WAVE_IMAGE
        variant['models'][0]['modelPropertiesResource']=variant['models'][0]['modelPropertiesResource'].replace('body_', 'body_wave_')
        vehicles.append(variant)
    for legacy in list(vehicles):
        metro=deepcopy(legacy)
        metro['id']=legacy['id'].replace('jinan_y1_', 'jinan_y1_metro_')
        metro['name']=legacy['name'].replace(' | ', ' · 新版LCD | ')
        legacy['name']=legacy['name'].replace(' | ', ' · 旧版LCD | ')
        vehicles.append(metro)
    displays={'id':'jinan_y1_displays','scriptLocations':[PREFIX+'scripts/displays.js'],'dataFetchMode':'ALL',
              'input':{'doorZ':DOOR_Z,'doorwayX':doorway_x,'doorwayY':doorway_y,'doorwayHalf':doorway_half,
                       'lcdWidth':LCD_WIDTH,'lcdLower':LCD_LOWER,'lcdUpper':LCD_UPPER,
                       'lcdOffset':LCD_OFFSET,'tvHalf':TV_HALF,'tvRows':TV_ROWS,'tvZ':TV_Z-TV_OFFSET}}
    dump(ROOT/'assets/mtr/mtr_custom_resources.json',{'vehicles':vehicles,'vehicleScripts':[displays],'rails':[
        {'id':'jinan_y1_steel_guideway','name':'济南云巴 | 钢制胶轮导轨梁','color':'9EAEB6',
         'modelResource':PREFIX+'models/steel_guideway.obj','textureResource':PREFIX+IMAGE,
         'flipTextureV':False,'repeatInterval':RAIL_PITCH,'modelYOffset':0}]})
    dump(ROOT/'pack.mcmeta',{'pack':{'pack_format':22,
        'description':'济南高新云巴Y1线 · MTR + JCM\nGPT-6.2-sol (high) 接入Codex制作'}})
    (ROOT/'dist').mkdir(exist_ok=True)
    with zipfile.ZipFile(ROOT/'dist/jinan_y1_mtr4_20261121_door_seam.zip','x',zipfile.ZIP_DEFLATED) as z:
        for p in [ROOT/'pack.mcmeta',ROOT/'pack.png',*sorted((ROOT/'assets').rglob('*'))]:
            if p.is_file():
                z.write(p,p.relative_to(ROOT).as_posix())


if __name__ == '__main__':
    build_pack()
