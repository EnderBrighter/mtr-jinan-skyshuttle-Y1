/* JCM 2.3 / MTR 4.0.5. Coordinates are supplied by the same generator as the model. */
var CFG = typeof SCRIPT_INPUT==='undefined' ? {} : SCRIPT_INPUT;
var W=1980,H=300,TV_W=880,TV_H=403,TV_FOOTER=44;
var BLUE=0x2464b7,LIGHT=0x78adf3,INK=0x263d54,GREY=0x8297a9,PAST=0xb1c2cc,RED=0xdf4054;
var METRO_CYAN=0x00aed4,METRO_PAPER=0xf2f7f8,METRO_INK=0x27343a;
var Color=java.awt.Color,Font=java.awt.Font;

function list(value){
    var result=[];
    if(value) for(var i=0;i<value.size();i++) result.push(value.get(i));
    return result;
}
function names(value){var s=String(value||'').split('|');return [s[0],s.slice(1).join(' / ')];}
function colour(g,c){g.setColor(new Color(Number(c)&0xffffff));}
function fill(g,x,y,w,h,c){colour(g,c);g.fill(new java.awt.geom.Rectangle2D.Double(x,y,w,h));}
function roundBox(g,x,y,w,h,r,c){colour(g,c);g.fill(new java.awt.geom.RoundRectangle2D.Double(x,y,w,h,r,r));}
function gradient(g,x,y,w,h,top,bottom){
    g.setPaint(new java.awt.GradientPaint(x,y,new Color(top),x,y+h,new Color(bottom)));
    g.fill(new java.awt.geom.Rectangle2D.Double(x,y,w,h));
}
function stroke(g,path,c,width){colour(g,c);g.setStroke(new java.awt.BasicStroke(width,1,1));g.draw(path);}
function path(){return new java.awt.geom.Path2D.Double();}
function line(g,x,y,X,Y,c,w){stroke(g,new java.awt.geom.Line2D.Double(x,y,X,Y),c,w);}
function dot(g,x,y,r,c){colour(g,c);g.fill(new java.awt.geom.Ellipse2D.Double(x-r,y-r,2*r,2*r));}
function text(g,value,x,y,size,c,max,bold,center){
    var s=String(value||'');if(!s)return;
    g.setFont(new Font('Microsoft YaHei',bold?1:0,size));colour(g,c);
    var width=g.getFontMetrics().stringWidth(s),scale=max&&width>max?max/width:1;
    var before=g.getTransform();g.translate(x-(center?width*scale/2:0),y);
    g.scale(scale,1);g.drawString(s,0,0);g.setTransform(before);
}
function pair(g,value,x,y,size,c,max,center){
    var p=names(value);text(g,p[0],x,y,size,c,max,true,center);
    text(g,p[1],x,y+Math.round(size*.65),Math.max(11,Math.round(size*.43)),c,max,false,center);
}
function mapLabel(g,value,x,y,c,max){
    var labels=names(value),size=12,en=labels[1],first=en,second='';
    text(g,labels[0],x,y,19,c,max,true,true);
    g.setFont(new Font('Microsoft YaHei',0,size));
    if(g.getFontMetrics().stringWidth(en)>max){
        var best=Infinity;
        for(var i=1;i<en.length-1;i++)if(en[i]===' '){
            var a=en.slice(0,i),b=en.slice(i+1),m=g.getFontMetrics();
            var width=Math.max(m.stringWidth(a),m.stringWidth(b));
            if(width<best){best=width;first=a;second=b;}
        }
    }
    text(g,first,x,y+13,size,c,max,false,true);
    text(g,second,x,y+26,size,c,max,false,true);
}
function aa(g){g.setRenderingHint(java.awt.RenderingHints.KEY_ANTIALIASING,java.awt.RenderingHints.VALUE_ANTIALIAS_ON);}
function shuttleMark(g,x,y,scale){
    var previous=g.getTransform(),mark=path();
    g.translate(x,y);g.scale(scale,scale);colour(g,INK);
    mark.moveTo(1,27);mark.curveTo(2,10,11,0,28,0);mark.curveTo(41,0,56,9,70,20);
    mark.curveTo(51,16,45,11,36,12);mark.curveTo(26,16,25,29,18,32);
    mark.curveTo(12,34,5,32,1,27);mark.closePath();g.fill(mark);
    var lower=path();lower.moveTo(2,31);lower.curveTo(16,40,40,25,67,29);
    lower.curveTo(53,38,29,42,14,39);lower.curveTo(7,38,3,36,2,31);
    lower.closePath();g.fill(lower);g.setTransform(previous);
    text(g,'云巴',x+82*scale,y+28*scale,Math.round(33*scale),INK,0,true,false);
    text(g,'SKYSHUTTLE',x+83*scale,y+40*scale,Math.round(10*scale),INK,0,true,false);
}
function metroMark(g,x,y,scale,c){
    // White-on-cyan seal in the car display, traced from the rail operator's 泉 mark.
    var tr=g.getTransform(),seal=path();
    g.translate(x,y);g.scale(scale/100,scale/100);
    seal.moveTo(13,0);seal.lineTo(87,0);seal.quadTo(100,0,100,13);
    seal.lineTo(100,87);seal.quadTo(100,100,87,100);
    seal.curveTo(76,100,72,93,72,81);seal.curveTo(72,67,82,57,82,44);
    seal.curveTo(82,26,69,14,54,10);seal.quadTo(50,3,46,10);
    seal.curveTo(31,14,18,26,18,44);seal.curveTo(18,57,28,67,28,81);
    seal.curveTo(28,93,24,100,13,100);seal.quadTo(0,100,0,87);
    seal.lineTo(0,13);seal.quadTo(0,0,13,0);seal.closePath();
    seal.moveTo(39,100);seal.curveTo(39,85,36,73,30,65);
    seal.curveTo(24,57,23,52,23,44);seal.curveTo(23,28,36,20,50,20);
    seal.curveTo(64,20,77,28,77,44);seal.curveTo(77,52,76,57,70,65);
    seal.curveTo(64,73,62,85,64,100);seal.lineTo(56,100);
    seal.curveTo(53,83,52,63,52,51);seal.curveTo(59,51,63,48,63,44);
    seal.curveTo(63,40,57,39,50,39);seal.curveTo(43,39,36,40,36,44);
    seal.curveTo(36,48,41,51,45,51);seal.curveTo(46,67,49,85,48,100);
    // The central T cutout opens at the bottom, between the two stems.
    seal.closePath();
    colour(g,c);g.fill(seal);g.setTransform(tr);
    text(g,'济南地铁',x+scale*1.20,y+scale*.59,Math.round(scale*.48),c,scale*2.23,true,false);
    text(g,'JINAN METRO',x+scale*1.24,y+scale*.87,Math.round(scale*.24),c,scale*2.13,true,false);
}
function transferName(value){var s=names(value)[0],m=s.match(/(?:^|\s)([0-9]+)\s*号?线/);return m?m[1]:s;}
function transfers(g,values,x,y){
    var ls=values.slice(0,4),width=34,total=ls.length*width;
    for(var i=0;i<ls.length;i++){
        var p=x-total/2+width*i;
        roundBox(g,p,y,width-4,19,5,ls[i].color);
        text(g,transferName(ls[i].name),p+(width-4)/2,y+15,13,0xffffff,width-7,true,true);
    }
}
function metroTransfers(g,values,x,y,large){
    var ls=values.slice(0,large?5:3),w=large?76:37,h=large?43:20;
    for(var i=0;i<ls.length;i++){
        var left=x-ls.length*w/2+i*w,number=transferName(ls[i].name),c=ls[i].color;
        roundBox(g,left,y,w-3,h,large?5:3,c);
        if(/^\d+$/.test(number)){
            text(g,number,left+w*.255,y+h*.77,large?33:15,0xffffff,w*.44,true,true);
            text(g,'号线',left+w*.63,y+h*.46,large?16:8,0xffffff,w*.48,true,true);
            text(g,'Line '+number,left+w*.64,y+h*.82,large?11:7,0xffffff,w*.49,false,true);
        }else{
            text(g,number,left+(w-3)/2,y+h*.70,large?19:11,0xffffff,w-8,true,true);
        }
    }
}

function circularDirection(mode){
    if(mode==='CLOCKWISE')return '顺时针|Clockwise';
    if(mode==='ANTICLOCKWISE')return '逆时针|Anticlockwise';
    return '';
}

function snapshot(vehicle,now){
    var on=vehicle.isOnRoute(),raw=vehicle.getThisRouteStops(),values=list(raw);
    var doorProgress=Math.min(1,Math.abs(Number(vehicle.getDoorValue()))),open=doorProgress>.015,step=0;
    if(values.length){
        step=Math.max(0,Math.min(values.length-1,Number(vehicle.getNextStopIndex(raw,.5))||0));
        if(open){
            var progress=Number(vehicle.getRailProgress()),best=6;
            for(var i=0;i<values.length;i++){
                var d=Number(values[i].distance),gap=Math.abs(d-progress);
                if(d>=0&&gap<best){best=gap;step=i;}
            }
        }
    }
    var selected=values[step],route=on&&selected?selected.route:null;
    var stops=values.map(function(s){
        return {name:s.station?String(s.station.getName()):String(s.name||'站名加载中'),transfers:list(s.routeInterchanges).map(function(r){return {name:String(r.name),color:Number(r.color)};})};
    });
    // MTR can list a station more than once on a non-circular route, e.g. a turnback.
    var mode=route?String(route.getCircularState()):'';
    var direction=circularDirection(mode),circular=Boolean(direction);
    var last=stops.length-1;
    var wraps=circular&&last>=2&&stops[0].name===stops[last].name;
    if(wraps)stops.pop();
    var index=stops.length?step%stops.length:0;
    var dest='';
    if(on&&selected&&mode==='NONE'){
        if(selected.destinationStation)dest=String(selected.destinationStation.getName());
        if(!dest)dest=String(selected.destinationName||'');
        if(!dest&&stops.length)dest=stops[stops.length-1].name;
    }
    return {on:on,open:open,stops:stops,index:index,mode:mode,direction:direction,circular:circular,
        destination:dest,time:now,doorProgress:doorProgress};
}

function twoDigits(value){return ('0'+value).slice(-2);}
function clock(date){return twoDigits(date.getHours())+':'+twoDigits(date.getMinutes());}
function tab(g,x,y){
    var p=path();p.moveTo(x-52,y);p.lineTo(x-39,y-7);p.lineTo(x+39,y-7);p.lineTo(x+52,y);
    p.closePath();colour(g,BLUE);g.fill(p);
}
function header(g,d,car,door){
    gradient(g,0,0,W,65,0xf2f7fc,0xdce9f7);fill(g,0,63,W,2,0xd2e3f2);
    shuttleMark(g,70,11,1.08);
    text(g,clock(new Date(d.time)),484,41,29,BLUE,115,true,true);tab(g,484,65);
    roundBox(g,662,7,870,48,16,0xeaf3fc);
    pair(g,d.open?'停靠站：|This station:':'下一站：|Next station:',695,27,25,INK,165,false);
    var label=names(d.on&&d.stops.length?d.stops[d.index].name:'—');
    g.setFont(new Font('Microsoft YaHei',1,34));
    var width=Math.min(380,g.getFontMetrics().stringWidth(label[0]));
    text(g,label[0],944,40,34,BLUE,380,true,false);
    text(g,label[1].toUpperCase(),959+width,39,18,INK,Math.max(152,1506-959-width),false,false);
    text(g,car+'车'+door+'门',1617,41,25,BLUE,124,true,true);tab(g,1617,65);
    if(d.circular||d.mode==='NONE'){
        var badge=new java.awt.geom.RoundRectangle2D.Double(1748,11,203,43,43,43);
        stroke(g,badge,0x79a8ec,4);
        var terminal=names(d.destination)[0];
        text(g,d.circular?names(d.direction)[0]+'运行':terminal?'终点站 '+terminal:'终点站',1849,40,23,BLUE,179,true,true);
    }
}

function metroHeader(g,d,car,door){
    fill(g,0,0,W,73,METRO_CYAN);
    fill(g,572,0,798,73,0xf5f8f9);
    fill(g,0,73,W,1,0xc5d9de);
    metroMark(g,33,9,54,0xffffff);
    pair(g,'济南云巴|JINAN SKYSHUTTLE',351,35,29,0xffffff,188,true);
    pair(g,d.open?'当前站|Current Station':'下一站|Next',680,35,28,METRO_INK,145,true);
    var current=d.on&&d.stops.length?d.stops[d.index].name:'—',label=names(current);
    pair(g,label[0]+'|'+label[1].toUpperCase(),1043,35,30,METRO_INK,565,true);
    if(d.circular){
        var direction=names(d.direction);
        pair(g,direction[0]+'|'+direction[1].toUpperCase(),1595,35,27,0xffffff,257,true);
    }else if(d.mode==='NONE'){
        pair(g,'终点站|Terminal',1425,32,17,0xffffff,85,true);
        var terminal=names(d.destination);
        pair(g,terminal[0]+'|'+terminal[1].toUpperCase(),1595,35,25,0xffffff,245,true);
    }
    roundBox(g,1816,14,124,43,7,0xeef9fc);
    text(g,car+'-'+door+'号门',1878,44,24,0x1486a3,112,false,true);
}

function loopLayout(d){
    var n=d.stops.length,order=[];
    var anchor=0;
    for(var i=0;i<n;i++)if(names(d.stops[i].name)[0]==='徐马'){anchor=i;break;}
    var before=names(d.stops[(anchor+n-1)%n].name)[0];
    var forward=before==='大正路'&&names(d.stops[anchor].name)[0]==='徐马'?-1:1;
    for(var i=0;i<n;i++)order.push((anchor+forward*i+n)%n);
    var positions=[],top=Math.ceil(n/2),bottom=n-top;
    for(var j=0;j<n;j++){
        var upper=j===0||j>bottom;
        var k=j===0?0:upper?n-j:j-1;
        var count=upper?top:bottom;
        positions[order[j]]={x:count===1?990:100+1780*k/(count-1),y:upper?144:221,upper:upper,order:j};
    }
    return positions;
}

function mapLayout(d){
    var n=d.stops.length,loop=d.circular&&n>1,pos=loop?loopLayout(d):[],indices=[];
    var len=loop?n:Math.min(n,32),start=loop?0:Math.max(0,Math.min(n-len,d.index-Math.floor(len/2)));
    var twoRows=loop||len>16,columns=twoRows?Math.ceil(len/2):len;
    var span=Math.min(1780,430*Math.max(0,columns-1)),left=(W-span)/2,right=W-left;
    for(var i=0;i<len;i++){
        var index=start+i;indices.push(index);
        if(!loop){
            var upper=!twoRows||i<columns;
            var offset=upper?i:i-columns;
            var x=span*offset/Math.max(1,columns-1);
            pos[index]={x:upper?left+x:right-x,y:twoRows?(upper?144:221):182,upper:upper};
        }
    }
    return {loop:loop,indices:indices,pos:pos,columns:columns,twoRows:twoRows};
}

function wholeMap(g,d,metro){
    var layout=mapLayout(d),indices=layout.indices,pos=layout.pos;
    if(metro&&layout.twoRows)indices.forEach(function(i){if(pos[i].upper)pos[i].y=154;});
    function passed(i){
        if(!layout.loop)return i<d.index;
        var n=d.stops.length,behind=(d.index-i+n)%n;
        return behind>0&&behind<=4;
    }
    for(var i=0;i<indices.length-(layout.loop?0:1);i++){
        var a=indices[i],b=indices[(i+1)%indices.length],p=pos[a],q=pos[b];
        var active=b===d.index&&(b>0||layout.loop);
        var c=active?RED:passed(b)?(metro?0xaab7b9:PAST):metro?METRO_CYAN:LIGHT;
        if(p.y===q.y){
            line(g,p.x,p.y,q.x,q.y,c,8);
            var dir=q.x>p.x?1:-1,mid=(p.x+q.x)/2;
            for(var band=-1;band<=1;band++){
                var x=mid+band*8;
                line(g,x-4*dir,p.y-5,x+3*dir,p.y,0xf3f9ff,2.5);
                line(g,x+3*dir,p.y,x-4*dir,p.y+5,0xf3f9ff,2.5);
            }
        }else{
            var left=layout.loop&&(p.order===0||q.order===0);
            if(layout.loop&&indices.length===2)left=i===0;
            var shoulder=left?100:1880,edge=left?39:1941,curve=path();
            curve.moveTo(p.x,p.y);curve.lineTo(shoulder,p.y);
            curve.curveTo(edge,p.y,edge,q.y,shoulder,q.y);curve.lineTo(q.x,q.y);
            stroke(g,curve,c,8);
            if(metro){
                var cx=(shoulder+3*edge)/4,cy=(p.y+q.y)/2,flow=q.y>p.y?1:-1;
                line(g,cx-4,cy-3*flow,cx,cy+3*flow,METRO_PAPER,2.5);
                line(g,cx,cy+3*flow,cx+4,cy-3*flow,METRO_PAPER,2.5);
            }
        }
    }
    for(var j=0;j<indices.length;j++){
        var i=indices[j],p=pos[i],s=d.stops[i],next=i===d.index;
        var past=passed(i),c=past?GREY:next?(metro?RED:BLUE):metro?METRO_INK:INK;
        if(metro){
            dot(g,p.x,p.y,10,next?RED:past?0xa0afb1:0x6199a4);
            dot(g,p.x,p.y,8,past?0xbdc9ca:METRO_PAPER);
            if(s.transfers.length)stroke(g,new java.awt.geom.Ellipse2D.Double(p.x-5,p.y-5,10,10),0x81aeb6,1);
        }else{
            if(next){dot(g,p.x,p.y,14,0xcde1ff);dot(g,p.x,p.y,9,0x649df3);}
            dot(g,p.x,p.y,next?4:8,past?PAST:BLUE);
        }
        var labelY=layout.twoRows?(p.upper?-42:30):38;
        var labelWidth=Math.max(27,Math.min(layout.twoRows?108:240,1760/Math.max(1,layout.columns-1)-7));
        mapLabel(g,s.name,p.x,p.y+labelY,c,labelWidth);
        var badgesY=p.y+(layout.twoRows&&p.upper?13:-31);
        if(metro)metroTransfers(g,s.transfers,p.x,badgesY,false);
        else transfers(g,s.transfers,p.x,badgesY);
    }
}

function doorsIcon(g,x,y,amount,on,scale){
    var transform=g.getTransform();
    g.translate(x,y);g.scale(scale||1,scale||1);x=0;y=0;
    var colourOn=on?BLUE:GREY;
    for(var side=-1;side<=1;side+=2){
        var left=x+side*(24+amount*24)-22;
        roundBox(g,left,y,44,78,3,0xc5d3df);
        gradient(g,left+4,y+5,36,43,on?0x567ca8:0x688298,0x365572);
        if(on){line(g,left+22-side*5,y+64,left+22+side*5,y+64,colourOn,3);
            line(g,left+22+side*5,y+64,left+22+side*1,y+60,colourOn,3);
            line(g,left+22+side*5,y+64,left+22+side*1,y+68,colourOn,3);}
    }
    g.setTransform(transform);
}

function localMap(g,d){
    var n=d.stops.length,points=[];
    for(var j=-1;j<=1;j++){
        var i=d.index+j;
        if(d.circular)i=(i+n)%n;
        if(i>=0&&i<n&&!points.some(function(p){return p.index===i;}))points.push({index:i,offset:j});
    }
    for(var i=1;i<points.length;i++)line(g,990+points[i-1].offset*340,175,990+points[i].offset*340,175,
        points[i].offset===0?RED:LIGHT,9);
    for(var i=0;i<points.length;i++){
        var p=points[i],x=990+p.offset*340,s=d.stops[p.index];
        if(p.offset===0){dot(g,x,175,15,0xbdd8ff);dot(g,x,175,10,0x639bf0);}
        dot(g,x,175,p.offset===0?4:8,p.offset<0?PAST:BLUE);
        transfers(g,s.transfers,x,137);pair(g,s.name,x,229,p.offset===0?35:27,
            p.offset<0?GREY:p.offset===0?BLUE:INK,313,true);
    }
    for(var s=-1;s<=1;s+=2){
        var x=990+s*775;
        line(g,990+s*588,114,990+s*588,263,0xdbe6ef,2);
        doorsIcon(g,x,112,0,false);
        pair(g,'车门关闭|Doors closed',x,231,24,BLUE,265,true);
    }
}

function openPage(g,d,key){
    var s=d.on&&d.stops.length?d.stops[d.index]:{name:'站名未提供|Station unavailable',transfers:[]};
    var on=key==='this'||key==='both',other=key==='other';
    var cn=key==='both'?'两侧开门':on?'本侧开门':other?'对侧开门':'请留意开门方向';
    var en=key==='both'?'Doors open on both sides':on?'Doors open on this side':other?'Doors open on the other side':'Check the platform side';
    if(other){
        doorsIcon(g,990,107,0,false,1.83);
        stroke(g,new java.awt.geom.Ellipse2D.Double(933,128,114,114),RED,10);
        line(g,953,148,1027,222,RED,10);
        for(var side=-1;side<=1;side+=2){
            var x=990+side*582;
            text(g,cn,x,181,42,BLUE,420,false,true);
            text(g,en,x,222,25,BLUE,555,false,true);
        }
        return;
    }
    var amount=on?d.doorProgress:0;
    if(s.transfers.length){
        pair(g,'可换乘|Transfer to',900,116,21,GREY,110,true);transfers(g,s.transfers,1008,104);
    }
    pair(g,s.name,990,198,54,INK,605,true);
    for(var side=-1;side<=1;side+=2){
        var x=990+side*630;
        doorsIcon(g,990+side*372,130,amount,on,1.15);
        text(g,cn,x,181,40,on?BLUE:INK,386,false,true);
        text(g,en,x,221,24,on?BLUE:INK,430,false,true);
    }
}

function metroOpenPage(g,d,key){
    var s=d.on&&d.stops.length?d.stops[d.index]:{name:'—',transfers:[]};
    var label=names(s.name);
    pair(g,label[0]+'|'+label[1].toUpperCase(),990,152,53,METRO_INK,850,true);
    if(s.transfers.length){
        var width=155+76*Math.min(5,s.transfers.length),left=(W-width)/2;
        pair(g,'出站换乘|Transfer via Exit',left+64,247,27,METRO_INK,140,true);
        metroTransfers(g,s.transfers,left+145+(width-155)/2,224,true);
    }
    var own=key==='this'||key==='both';
    var note=key==='both'?'两侧开门|Doors open on both sides':
        own?'本侧开门|Doors open on this side':
        key==='other'?'对侧开门|Doors open on the other side':'请留意开门方向|Check the platform side';
    for(var side=-1;side<=1;side+=2){
        var x=990+side*758;
        doorsIcon(g,x,94,own?d.doorProgress:0,own,1.5);
        if(key==='other'){
            stroke(g,new java.awt.geom.Ellipse2D.Double(x-39,113,78,78),RED,7);
            line(g,x-24,128,x+24,176,RED,7);
        }
        var message=names(note);
        text(g,message[0],x,258,34,METRO_INK,400,false,true);
        text(g,message[1],x,283,20,METRO_INK,407,false,true);
    }
}

function paintLCD(g,d,key,car,door,page,metro){
    aa(g);
    if(metro){
        fill(g,0,0,W,H,METRO_PAPER);
        metroHeader(g,d,car,door);
    }else{
        gradient(g,0,0,W,H,0xf0f6fc,0xe9f3fb);
        header(g,d,car,door);
    }
    if(d.open){if(metro)metroOpenPage(g,d,key);else openPage(g,d,key);return;}
    if(!d.on||!d.stops.length)pair(g,d.on?'正在读取站点|Loading stops':'暂不载客|Not in service',W/2,180,42,INK,1350,true);
    else if(!metro&&page==='near')localMap(g,d);
    else wholeMap(g,d,metro);
}

function tvStation(g,value,y){
    var label=names(value),x=110,word=label[1].toUpperCase(),first=word,second='';
    text(g,label[0]||'—',x,y,26,INK,206,true,true);
    g.setFont(new Font('Microsoft YaHei',0,16));
    if(g.getFontMetrics().stringWidth(word)>202){
        var split=word.lastIndexOf(' ',Math.ceil(word.length*.6));
        if(split>0){first=word.slice(0,split);second=word.slice(split+1);}
    }
    text(g,first,x,y+24,16,INK,202,false,true);
    text(g,second,x,y+43,16,INK,202,false,true);
    roundBox(g,x-23,y+51,46,3,4,BLUE);
}

function paintTV(g,d){
    aa(g);gradient(g,0,0,TV_W,TV_H,0xe9edf3,0xe1e7ef);
    gradient(g,0,0,TV_W,48,0xf3f5f8,0xe5e8ec);
    metroMark(g,42,6,36,0x166b9d);
    var date=new Date(d.time);
    var dateString=date.getFullYear()+'-'+twoDigits(date.getMonth()+1)+'-'+twoDigits(date.getDate());
    text(g,dateString+'   '+clock(date),653,34,23,INK,375,false,true);
    gradient(g,0,48,222,TV_H-TV_FOOTER-48,0xe8edf4,0xd3dfed);
    fill(g,222,48,TV_W-222,TV_H-TV_FOOTER-48,0x000000);
    pair(g,d.open?'停靠站|This Station':'下一站|Next Station',110,80,21,INK,190,true);
    var station=d.on&&d.stops.length?d.stops[d.index].name:'';
    tvStation(g,station,145);
    if(d.circular||d.mode==='NONE'){
        pair(g,d.circular?'运行方向|Running Direction':'终点站|Terminal',110,232,21,INK,196,true);
        tvStation(g,d.circular?d.direction:d.destination,294);
    }
}

function paintTicker(g,elapsed){
    aa(g);gradient(g,0,0,TV_W,TV_FOOTER,0xe9edf2,0xd8e4f0);
    g.setFont(new Font('Microsoft YaHei',1,25));
    var message='欢迎乘坐济南云巴！',width=g.getFontMetrics().stringWidth(message);
    var x=TV_W-(Math.floor(elapsed/7)%(TV_W+width+45));
    text(g,message,x,32,25,INK,0,true,false);
}

function doorSide(v,car,side,screenZ){
    // The draw transform flips X and Z relative to the native platform probe.
    var z=-screenZ,half=CFG.doorwayHalf,x=CFG.doorwayX,y=CFG.doorwayY;
    function opens(sign){
        var left=sign>0?x[0]:-x[1],right=sign>0?x[1]:-x[0];
        return v.isDoorOpenable(car,new Vector3f(left,y[0],z-half),new Vector3f(right,y[1],z+half));
    }
    var own=opens(-side),opposite=opens(side);
    return own?(opposite?'both':'this'):(opposite?'other':'unknown');
}

function lcdCall(tex,side,z){
    var a=CFG.lcdLower,b=CFG.lcdUpper,offset=CFG.lcdOffset,half=CFG.lcdWidth/2;
    function point(p,end){return new Vector3f(side*(p[0]-offset),p[1]-1,z+end);}
    var left=-side*half,right=-left;
    return QuadDrawCall.create('Y1 door LCD').quad(point(b,left),point(a,left),point(a,right),point(b,right)).texture(tex.identifier).renderType('LIGHT');
}

function tvCall(tex,orient,footer){
    var h=CFG.tvHalf,a=CFG.tvRows[0],b=CFG.tvRows[1],z=CFG.tvZ;
    if(footer){b=a+(b-a)*TV_FOOTER/TV_H;z-=.0016;}
    function point(x,y){return new Vector3f(orient*x,y-1,orient*z);}
    return QuadDrawCall.create(footer?'Y1 TV ticker':'Y1 passenger TV')
        .quad(point(h,b),point(h,a),point(-h,a),point(-h,b)).texture(tex.identifier).renderType('LIGHT');
}

function create(ctx,state){
    state.lcd={};state.keys={};state.calls=[];state.next=0;state.nextTicker=0;state.tickerStart=Date.now();
    state.tv=new GraphicsTexture(TV_W,TV_H);state.ticker=new GraphicsTexture(TV_W,TV_FOOTER);
}
function render(ctx,state,v){
    var now=Date.now();
    if(now>=state.next){
        state.next=now+200;
        var d=snapshot(v,now),cars=ctx.getMyCars(),calls=[];
        var page=Math.floor(now/7200)%2?'near':'full',active={};
        var minute=Math.floor(now/60000),name=d.stops.length?d.stops[d.index].name:'';
        var tvKey=JSON.stringify([d.on,d.open,d.mode,d.destination,name,minute]);
        if(state.tvKey!==tvKey){
            state.tvKey=tvKey;paintTV(state.tv.graphics,d);state.tv.upload();
        }
        var lcdKey=JSON.stringify([d.on,d.open,d.stops,d.index,d.mode,d.destination,Math.round(d.doorProgress*12),minute]);
        for(var i=0;i<cars.length;i++){
            var car=Number(cars[i]),id=String(v.getVehicleId(car)),metro=id.indexOf('jinan_y1_metro_')===0;
            // OBJ cars use a 180-degree local yaw on the A end. The draw call applies its own X rotation.
            var orientation=/_rear$/.test(id)?1:-1,z=orientation*CFG.doorZ;
            calls.push({car:car,draw:tvCall(state.tv,orientation,false)});
            calls.push({car:car,draw:tvCall(state.ticker,orientation,true)});
            for(var side=-1;side<=1;side+=2){
                var number=side*orientation<0?1:2,index=car+':'+number;
                var key=d.open?doorSide(v,car,side,z):'closed';
                var imageKey=lcdKey+'|'+key+'|'+(metro?'metro':d.open?'open':page);
                if(!state.lcd[index])state.lcd[index]=new GraphicsTexture(W,H);
                var tex=state.lcd[index];active[index]=true;
                if(state.keys[index]!==imageKey){
                    state.keys[index]=imageKey;paintLCD(tex.graphics,d,key,car+1,number,page,metro);tex.upload();
                }
                calls.push({car:car,draw:lcdCall(tex,side,z)});
            }
        }
        Object.keys(state.lcd).forEach(function(index){if(!active[index]){state.lcd[index].close();delete state.lcd[index];delete state.keys[index];}});
        state.calls=calls;
    }
    if(state.calls.length&&now>=state.nextTicker){
        state.nextTicker=now+40;
        paintTicker(state.ticker.graphics,now-state.tickerStart);state.ticker.upload();
    }
    for(var i=0;i<state.calls.length;i++){
        var item=state.calls[i],manager=ctx.getCarRenderManager(item.car);
        if(manager)manager.draw(item.draw);
    }
}
function dispose(ctx,state){
    Object.keys(state.lcd||{}).forEach(function(key){state.lcd[key].close();});
    if(state.tv)state.tv.close();
    if(state.ticker)state.ticker.close();
    state.calls=[];
}
