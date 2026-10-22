"""Analyze phase-2 evidence without inference; keep metrics and visual gates separate."""
import argparse,csv,hashlib,html,json,math,random,shutil
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageOps


def images(folder,mode='RGB'):
    return np.stack([np.asarray(Image.open(p).convert(mode)) for p in sorted(folder.glob('*.png'))])


def video(path):
    cap=cv2.VideoCapture(str(path));frames=[];fps=cap.get(cv2.CAP_PROP_FPS)
    while True:
        ok,im=cap.read()
        if not ok:break
        frames.append(cv2.cvtColor(im,cv2.COLOR_BGR2RGB))
    cap.release();return np.stack(frames),fps


def component(rgb,color,roi=None):
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV);lo,hi={'green':(35,85),'blue':(95,135),'yellow':(10,35)}[color]
    mask=((hsv[:,:,0]>=lo)&(hsv[:,:,0]<=hi)&(hsv[:,:,1]>=80)&(hsv[:,:,2]>=50)).astype(np.uint8)
    if roi is not None:mask*=roi.astype(np.uint8)
    n,labels,stats,centers=cv2.connectedComponentsWithStats(mask,8)
    if n<2:return None
    j=1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
    if stats[j,cv2.CC_STAT_AREA]<20:return None
    return {'center':centers[j].tolist(),'area':int(stats[j,cv2.CC_STAT_AREA])}


def error(a,b,region):
    values=np.abs(a.astype(np.float32)-b.astype(np.float32))[region].ravel()
    if not values.size:return None
    return {'mae_255':float(values.mean()),'p95_255':float(np.percentile(values,95)),'max_255':float(values.max())}


def two_hand_diagnostic(run,raw,case):
    """Fixture-specific skin-extrema heuristic; inspect overlays, not pose truth."""
    expected=case.get('annotations',{}).get('two_hand_endpoints')
    if not expected:return None
    n,h,w=raw.shape[:3];records=[];errors=[]
    sheet=Image.new('RGB',(5*260,math.ceil(n/5)*290),'white');draw=ImageDraw.Draw(sheet)
    for i,rgb in enumerate(raw):
        roi=np.zeros((h,w),bool);roi[int(.37*h):int(.72*h),int(.39*w):int(.62*w)]=True
        torso=component(rgb,'blue',roi);im=Image.fromarray(rgb);d=ImageDraw.Draw(im);points=[]
        if torso:
            center=np.asarray(torso['center']);shift=center-np.asarray([190.5/384*w,170/320*h])
            r,g,b=[rgb[:,:,j].astype(float) for j in range(3)]
            skin=(r>155)&(g>100)&(r>g*1.15)&(g>b*1.12)
            xx=np.arange(w)[None,:];yy=np.arange(h)[:,None];skin&=yy>.35*h
            for j,side in enumerate((-1,1)):
                keep=skin&((xx<center[0]-.08*w) if side<0 else (xx>center[0]+.08*w))
                y,x=np.where(keep);wanted=np.asarray(expected[i][j])*[w,h]+shift
                d.ellipse((wanted[0]-5,wanted[1]-5,wanted[0]+5,wanted[1]+5),outline='lime',width=2)
                if len(x)<10:points.append(None);continue
                candidates=np.stack([x,y],1);shoulder=np.asarray([(190+side*29)/384*w,137/320*h])+shift
                extreme=candidates[np.argsort(np.linalg.norm(candidates-shoulder,axis=1))[-12:]].mean(0)
                value=float(np.linalg.norm(extreme-wanted)/math.hypot(w,h));errors.append(value)
                points.append({'endpoint_px':extreme.tolist(),'expected_aligned_px':wanted.tolist(),'error_diagonal':value})
                d.ellipse((extreme[0]-5,extreme[1]-5,extreme[0]+5,extreme[1]+5),outline='red',width=2)
        records.append({'frame':i,'points':points})
        sheet.paste(ImageOps.pad(im,(260,260)),((i%5)*260,(i//5)*290));draw.text(((i%5)*260+3,(i//5)*290+263),str(i),fill='black')
    sheet.save(run/'two-hand-overlays.jpg')
    result={'method':'Blue torso translation plus skin-color extrema, specific to this original drawing. Ambiguous with duplicate arms. Not an independent pose estimator. Inspect every overlay.','points':records,'valid_points':len(errors),'expected_points':2*n,'mean_error_diagonal':float(np.mean(errors)) if errors else None,'max_error_diagonal':max(errors) if errors else None}
    (run/'two-hand-diagnostics.json').write_text(json.dumps(result,indent=2), encoding='utf-8');return result


def compare(a,b):
    def digest(x):return hashlib.sha256(x.tobytes()).hexdigest()
    x,y=np.load(a/'inputs/conditioning.npz'),np.load(b/'inputs/conditioning.npz')
    conditioning={k:{'a_sha256':digest(x[k]),'b_sha256':digest(y[k]),'a_shape':list(x[k].shape),'b_shape':list(y[k].shape),'equal':bool(x[k].shape==y[k].shape and np.array_equal(x[k],y[k]))} for k in x.files}
    ga=json.loads((a/'workflow-api.json').read_text(encoding='utf-8'));gb=json.loads((b/'workflow-api.json').read_text(encoding='utf-8'))
    changes={k:{'a':ga.get(k),'b':gb.get(k)} for k in ga.keys()|gb.keys() if ga.get(k)!=gb.get(k)}
    u,v=images(a/'raw'),images(b/'raw');same=u.shape==v.shape
    return {'a':a.name,'b':b.name,'conditioning':conditioning,'graph_node_changes':changes,
            'same_output_shape':same,'raw_pixels_equal':bool(same and np.array_equal(u,v)),
            'raw_mae_255':float(np.abs(u.astype(float)-v.astype(float)).mean()) if same else None}


def analyze(run):
    info=json.loads((run/'fidelity.json').read_text(encoding='utf-8'));case=info['case'];source=images(run/'inputs/source');raw=images(run/'raw');comp=images(run/'composite')
    mask=images(run/'inputs/masks','L')>0;n,h,w=raw.shape[:3];decoded,fps=video(run/'composite.mp4')
    outside=~mask;safe=np.stack([~cv2.dilate(m.astype(np.uint8),np.ones((17,17),np.uint8)).astype(bool) for m in mask])
    png=error(comp,source,outside);raw_error=error(raw,source,safe);encoded=error(decoded,source,safe) if decoded.shape==source.shape else None
    record={'run':run.name,'case':case['id'],'profile':info['profile'],'seed':info['seed'],'mode':case.get('mode','motion-transfer'),
            'width':w,'height':h,'frames':n,'fps':fps,'technical_pass':n==case.get('frames',17) and raw.shape==source.shape==comp.shape==decoded.shape and abs(fps-8)<.01,
            'worker_seconds':info['worker_elapsed_seconds'],'composite_png_outside':png,'raw_outside_dilated_mask':raw_error,'encoded_outside_dilated_mask':encoded,
            'outside_png_pass':png['max_255']==0 if png else None,'raw_preservation_pass':raw_error['mae_255']<=3 and raw_error['p95_255']<=10 if raw_error else None,
            'encoded_preservation_pass':encoded['mae_255']<=3 and encoded['p95_255']<=10 if encoded else None,'visual_scores_are_separate':True}
    samples=[]
    for line in (run/'gpu.csv').read_text(encoding='utf-8').splitlines()[1:]:
        try:
            f=line.split(',');samples.append([float(f[2]),float(f[3]),float(f[4]),float(f[5])])
        except (ValueError,IndexError):pass
    if samples:
        arr=np.asarray(samples);record.update(sampled_peak_vram_MiB=float(arr[:,1].max()),mean_gpu_utilization_percent=float(arr[:,0].mean()),mean_power_W=float(arr[:,2].mean()),sampled_peak_process_tree_rss_MiB=float(arr[:,3].max()),resource_samples=len(samples))
    found=[];distance=[];annot=case.get('annotations',{})
    if record['mode']=='object-swap':
        for i,frame in enumerate(raw):
            c=component(frame,annot.get('target_color','green'),mask[i]);found.append(c)
            expected=annot.get('expected_centers',[])
            if c and i<len(expected) and expected[i] is not None:distance.append(float(np.linalg.norm(np.asarray(c['center'])-np.asarray(expected[i])*[w,h])/math.hypot(w,h)))
        record['target_color_fraction']=sum(c is not None for c in found)/n
        record['centroid_mean_error_diagonal']=float(np.mean(distance)) if distance else None
    sheet=Image.new('RGB',(5*260,math.ceil(n/5)*290),'white');d=ImageDraw.Draw(sheet)
    for i,frame in enumerate(raw):
        im=Image.fromarray(frame);draw=ImageDraw.Draw(im)
        if found and found[i]:
            x,y=found[i]['center'];draw.ellipse((x-5,y-5,x+5,y+5),outline='red',width=2)
        expected=annot.get('expected_centers',[])
        if i<len(expected) and expected[i] is not None:
            x,y=np.asarray(expected[i])*[w,h];draw.ellipse((x-6,y-6,x+6,y+6),outline='lime',width=2)
        sheet.paste(ImageOps.pad(im,(260,260)),((i%5)*260,(i//5)*290));d.text(((i%5)*260+3,(i//5)*290+263),str(i),fill='black')
    sheet.save(run/'diagnostic-all-frames.jpg');(run/'quality-metrics.json').write_text(json.dumps(record,indent=2), encoding='utf-8')
    hands=two_hand_diagnostic(run,raw,case)
    if hands:
        record['two_hand_mean_error_diagonal']=hands['mean_error_diagonal'];record['two_hand_valid_points']=hands['valid_points']
        (run/'quality-metrics.json').write_text(json.dumps(record,indent=2), encoding='utf-8')
    return record


def packet(root,runs,public_only):
    folder=root/('public-review' if public_only else 'private-review');folder.mkdir(exist_ok=True)
    allowed=set(json.loads((root/'publication-clearance.json').read_text(encoding='utf-8'))['public_case_ids']) if (root/'publication-clearance.json').exists() else set()
    runs=[r for r in runs if not public_only or json.loads((r/'fidelity.json').read_text(encoding='utf-8'))['case']['id'] in allowed]
    random.Random(217306).shuffle(runs);key=[];cards=[];rows=[]
    for i,run in enumerate(runs,1):
        ident=f'sample-{i:02d}';dest=folder/ident;dest.mkdir(exist_ok=True)
        for a,b in [('source.mp4','source.mp4'),('generated.mp4','raw.mp4'),('composite.mp4','finished.mp4'),('inputs/reference.png','reference.png')]:shutil.copyfile(run/a,dest/b)
        key.append({'sample':ident,'run':run.name,'metadata_sha256':hashlib.sha256((run/'fidelity.json').read_bytes()).hexdigest()})
        for stage in ('raw','finished'):
            rows.append(dict(sample=ident,stage=stage,reviewer='',fidelity_0_4='',motion_0_4='',stability_0_4='',anatomy_0_4='',photorealism_0_4_or_NA='',acceptable_frames='',catastrophic_frames='',notes=''))
        media=f'<div><b>Reference</b><img src="{ident}/reference.png"></div>'+''.join(f'<div><b>{label}</b><video controls loop muted src="{ident}/{name}.mp4"></video></div>' for label,name in [('Source','source'),('Raw','raw'),('Finished','finished')])
        cards.append(f'<article><h2>{ident}</h2><div class="row">{media}</div></article>')
    rubric=(root/'RUBRIC.md').read_text(encoding='utf-8')
    (folder/'RUBRIC.md').write_text(rubric, encoding='utf-8')
    (root/('public-unblinding-key.json' if public_only else 'private-unblinding-key.json')).write_text(json.dumps(key,indent=2), encoding='utf-8')
    if rows:
        with (folder/'review.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    label='Redistributable test packet' if public_only else 'Private research packet — includes media not cleared for publication'
    (folder/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Blinded review</title><style>body{font:16px system-ui;background:#eee;margin:24px}article{background:white;padding:16px;margin:20px 0}.row{display:flex;gap:12px;flex-wrap:wrap}.row>div{width:23%;min-width:220px}img,video{width:100%;height:300px;object-fit:contain;background:#ddd}pre{white-space:pre-wrap;max-width:1000px}</style><h1>'+label+'</h1><p>Score all frames and both stages before opening the separate unblinding key. No independent review has yet occurred. Source aspect, fitting and resolution may reveal a condition; blinding conceals labels only.</p><details><summary>Frozen rubric</summary><pre>'+html.escape(rubric)+'</pre></details>'+''.join(cards), encoding='utf-8')


def main(root,runs_name='runs'):
    root=Path(root);runs=[p for p in sorted((root/runs_name).iterdir()) if (p/'fidelity.json').exists() and json.loads((p/'fidelity.json').read_text(encoding='utf-8')).get('status','succeeded')=='succeeded']
    records=[analyze(p) for p in runs];lookup={r.name:r for r in runs};pairs=[]
    for a,b in [('sheet','crop'),('crop','describe'),('describe','separate'),('separate','native'),('native','cover'),('cover','fullbody'),('crop','production')]:
        x,y=f'portrait__{a}__s42',f'portrait__{b}__s42'
        if x in lookup and y in lookup:pairs.append(compare(lookup[x],lookup[y]))
    for name in ('new-synthetic-motion','new-real-motion'):
        a,b=name+'__baseline__s42',name+'__candidate__s42'
        if a in lookup and b in lookup:pairs.append(compare(lookup[a],lookup[b]))
    (root/'quality-metrics.json').write_text(json.dumps(records,indent=2), encoding='utf-8');(root/'paired-quality-analysis.json').write_text(json.dumps(pairs,indent=2), encoding='utf-8')
    if records:
        keys=sorted(set().union(*(r.keys() for r in records)))
        with (root/'quality-metrics.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(records)
    packet(root,runs,False);packet(root,runs,True)
    print(f'{len(records)} runs; {len(pairs)} contrasts; private/public packets separated. Visual scores remain required.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root');p.add_argument('--runs-name',default='runs');a=p.parse_args();main(a.root,a.runs_name)
