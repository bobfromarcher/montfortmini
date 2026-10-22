"""Build four small prospective cases; no inference or quality-based selection.

Requires the two original recordings and their Commons imageinfo JSON records.
The saved input hashes, rather than a fresh encode on another FFmpeg build,
are authoritative for exact replay. Synthetic art is original MIT code.
"""
import argparse, datetime, hashlib, json, math, shutil, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import numpy as np


def run(args):
    subprocess.run(args, check=True, capture_output=True, timeout=90)


def actor(t, reference=False):
    im=Image.new('RGB',(384,320),(225,232,235));d=ImageDraw.Draw(im)
    d.rectangle((0,281,384,320),fill=(183,192,198))
    skin=(220,168,126);shirt=(34,88,200) if reference else (38,135,82)
    d.ellipse((145,276,235,292),fill=(150,157,162))
    d.line([(174,210),(169,277)],fill=(66,42,59),width=18)
    d.line([(207,210),(215,277)],fill=(66,42,59),width=18)
    d.rounded_rectangle((158,272,180,286),radius=4,fill=(35,35,38))
    d.rounded_rectangle((204,272,227,286),radius=4,fill=(35,35,38))
    d.rounded_rectangle((160,122,221,218),radius=12,fill=shirt)
    points=[]
    for side in (-1,1):
        angle=.25+1.3*math.sin(math.pi*t)
        shoulder=(190+side*29,137)
        elbow=(shoulder[0]+side*38*math.sin(angle),137+38*math.cos(angle))
        hand=(elbow[0]+side*30*math.sin(angle+.2),elbow[1]+30*math.cos(angle+.2))
        d.line([shoulder,elbow,hand],fill=skin,width=12)
        d.ellipse((hand[0]-6,hand[1]-6,hand[0]+6,hand[1]+6),fill=skin)
        points.append([hand[0]/384,hand[1]/320])
    d.rectangle((180,109,200,127),fill=skin)
    d.ellipse((165,66,216,120),fill=skin)
    d.pieslice((164,61,217,106),180,360,fill=(120,60,30) if reference else (38,32,27))
    for x in (178,202):d.ellipse((x,87,x+4,92),fill=(30,30,30))
    d.arc((181,94,201,109),0,180,fill=(110,55,44),width=2)
    return im,points


def sphere_reference():
    y,x=np.mgrid[:320,:320];dx=(x-160)/80;dy=(y-160)/80
    z=np.sqrt(np.clip(1-dx*dx-dy*dy,0,1));light=np.clip(.35+.55*z-.16*dx-.2*dy,.1,1)
    arr=np.full((320,320,3),231,dtype=np.uint8);mask=dx*dx+dy*dy<=1
    col=np.stack([45*light,190*light,65*light],-1).astype(np.uint8);arr[mask]=col[mask]
    return Image.fromarray(arr)


def main(raw,output):
    raw=Path(raw);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    cases={}
    for ident,mode in [('new-synthetic-object','object-swap'),('new-synthetic-motion','motion-transfer'),('new-real-object','object-swap'),('new-real-motion','motion-transfer')]:
        dest=output/ident;dest.mkdir(exist_ok=True);frames=dest/'frames';frames.mkdir(exist_ok=True)
        annotations={'target_color':'green' if mode=='object-swap' else 'blue'}
        provenance={'author':'montfortmini contributors','license':'MIT','source':'original procedural art, new trajectory and two-arm renderer'}
        notes=[]
        bbox=end=[0,0,1,1]
        if ident=='new-synthetic-object':
            for i in range(17):
                cy=110+85*i/16
                im=Image.new('RGB',(384,320),(226,229,232));d=ImageDraw.Draw(im)
                for x in range(0,384,48):d.line((x,0,x,320),fill=(209,214,219))
                for y in range(0,320,40):d.line((0,y,384,y),fill=(209,214,219))
                d.ellipse((170,cy+20,236,cy+40),fill=(155,160,165))
                d.rectangle((162,cy-24,214,cy+28),fill=(195,52,48),outline=(115,27,24),width=2)
                im.save(frames/f'{i:04d}.png')
                annotations.setdefault('expected_centers',[]).append([188/384,(cy+2)/320])
            bbox=[.39,.24,.22,.26];end=[.39,.505625,.22,.26]
            sphere_reference().save(dest/'reference.png')
            prompt='A single smooth solid green sphere shown in the reference moves straight downward over a pale gray grid. Preserve its vertical trajectory and size. Fixed camera.'
        elif ident=='new-synthetic-motion':
            for i in range(17):
                im,points=actor(i/16);im.save(frames/f'{i:04d}.png')
                annotations.setdefault('two_hand_endpoints',[]).append(points)
            actor(0,True)[0].save(dest/'reference.png')
            prompt='An illustrated brown-haired person in a blue shirt raises both arms outward and then lowers both arms, following the source timing. Full body, one person, fixed camera.'
            notes.append('New two-arm sequence shares procedural-art assumptions with earlier fixtures; not an independent real-world domain.')
        else:
            name='bee' if mode=='object-swap' else 'pushup'
            provenance=json.loads((raw/(name+'.json')).read_text(encoding='utf-8'))
            start=2 if name=='bee' else 71
            filt='fps=8,scale=480:-2'
            run(['ffmpeg','-y','-loglevel','error','-ss',str(start),'-i',str(raw/(name+'.webm')),'-vf',filt,'-frames:v','17','-start_number','0',str(frames/'%04d.png')])
            notes.append(f'Independent original recording {name}; source interval {start}..{start+2.125}s; filter {filt}; audio removed.')
            if name=='bee':
                bbox=end=[.28,.32,.22,.43]
                sphere_reference().save(dest/'reference.png')
                prompt='Replace only the yellow ball inside the selected region with the single smooth solid green sphere in the reference. Keep the scene lighting, size, and position. Fixed camera.'
                annotations['expected_centers']=[[.382,.54] for _ in range(17)]
                notes.append('Stationary target with nearby independently moving bee; assesses fidelity and preservation, not a moving-object trajectory.')
            else:
                actor(0,True)[0].save(dest/'reference.png')
                prompt='The illustrated brown-haired person in a blue shirt performs the same side-view push-up motion as the source athlete, hands planted on the ground, body horizontal. One character, natural articulated motion.'
                annotations['phase_samples']={'0':'high plank, elbows extended','4':'high plank, elbows extended','8':'high plank, elbows extended','12':'lowering to ground, elbows bent','16':'low position, elbows bent'}
                notes.append('Real driving to original illustrated reference: cross-domain motion stress, not a photorealistic identity holdout. Continuous close camera angle, no temporal cuts in the selected interval; no facial identity claim.')
        run(['ffmpeg','-y','-loglevel','error','-framerate','8','-i',str(frames/'%04d.png'),'-frames:v','17','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(dest/'input.mp4')])
        (dest/'source-provenance.json').write_text(json.dumps(provenance,indent=2), encoding='utf-8')
        cases[ident]={'id':ident,'split':'prospective-held-out','kind':ident.removeprefix('new-'),'mode':mode,'video':f'new-tests/{ident}/input.mp4','reference':f'new-tests/{ident}/reference.png','frames':17,'prompt':prompt,'bbox':bbox,'end_bbox':end,'annotations':annotations,'notes':notes,'sha256':{k:hashlib.sha256((dest/f).read_bytes()).hexdigest() for k,f in [('video','input.mp4'),('reference','reference.png')]}}
    (output/'cases.json').write_text(json.dumps(cases,indent=2), encoding='utf-8')
    # Same source-only annotation used in the saved revision-2 freeze.
    from quality_analysis import component
    spec=cases['new-real-object'];centers=[]
    for path in sorted((output/'new-real-object/frames').glob('*.png')):
        rgb=np.asarray(Image.open(path).convert('RGB'));h,w=rgb.shape[:2];roi=np.zeros((h,w),bool)
        roi[int(.32*h):int(.75*h),int(.28*w):int(.50*w)]=True
        found=component(rgb,'yellow',roi)
        if not found:raise ValueError('Missing source-only yellow-ball annotation')
        centers.append((np.asarray(found['center'])/[w,h]).tolist())
    spec['annotations']['expected_centers']=centers
    spec['annotations']['centroid_method']='Largest yellow/orange component inside preselected ROI; source-only overlay retained. Diagnostic annotation, not an independent human label.'
    (output/'cases.json').write_text(json.dumps(cases,indent=2), encoding='utf-8')
    (output/'inputs-frozen.json').write_text(json.dumps({'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cases':cases,'generated_outputs_inspected':False},indent=2), encoding='utf-8')
    (output.parent/'quality-cases.json').write_text(json.dumps(cases,indent=2), encoding='utf-8')
    print('Prepared four prospective cases; inspect and annotate source only before inference.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--raw',required=True);p.add_argument('--output',required=True);a=p.parse_args();main(a.raw,a.output)
