"""Auditable paired pixel/conditioning contrasts and bounded resource summaries."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageOps
from metrics import target_component

def frames(run,kind='raw'):
    return np.stack([np.asarray(Image.open(p).convert('RGB')) for p in sorted((run/kind).glob('*.png'))])

def compare(a,b):
    x,y=frames(a),frames(b)
    result={'a':a.name,'b':b.name,'same_shape':x.shape==y.shape}
    if x.shape==y.shape:
        d=np.abs(x.astype(float)-y.astype(float));result.update(raw_pixels_equal=bool(np.array_equal(x,y)),raw_mae_255=float(d.mean()),raw_max_255=float(d.max()))
    xa,xb=np.load(a/'inputs/conditioning.npz'),np.load(b/'inputs/conditioning.npz')
    result['conditioning']={}
    for k in xa.files:
        u,v=xa[k],xb[k];entry={'a_shape':list(u.shape),'b_shape':list(v.shape),'a_sha256':hashlib.sha256(u.tobytes()).hexdigest(),'b_sha256':hashlib.sha256(v.tobytes()).hexdigest()}
        if u.shape==v.shape:entry.update(equal=bool(np.array_equal(u,v)),mae=float(np.abs(u-v).mean()))
        result['conditioning'][k]=entry
    return result

def motion_landmarks(run):
    """Skin endpoint heuristic; export every point for visual checking, never call it pose truth."""
    info=json.loads((run/'evaluation.json').read_text());case=info['case']
    if case['kind']!='synthetic-motion':return None
    raw=frames(run);h,w=raw.shape[1:3];left=case['split']=='held-out';points=[];errors=[]
    sheet=Image.new('RGB',(5*240,4*260),'white');draw=ImageDraw.Draw(sheet)
    for i,rgb in enumerate(raw):
        roi=np.zeros((h,w),dtype=bool);roi[int(.37*h):int(.66*h),int(.39*w):int(.60*w)]=True
        torso=target_component(rgb,case['annotations']['target_color'],roi)
        if torso is None:points.append(None);continue
        center=np.asarray(torso['center']);expected=np.asarray(case['annotations']['moving_endpoint'][i])*[w,h]
        # Original torso drawing center: (160,167.5)/320; translate only.
        shift=center-np.asarray([.5*w,167.5/320*h]);shoulder=np.asarray([(135 if left else 185)/320*w,136/320*h])+shift
        r,g,b=[rgb[:,:,j].astype(float) for j in range(3)]
        skin=(r>170)&(g>120)&(r>1.15*g)&(g>1.15*b)
        xx=np.arange(w)[None,:];skin&=(xx<center[0]-.09*w) if left else (xx>center[0]+.09*w)
        yy,xx=np.where(skin)
        if len(xx)<10:points.append(None);continue
        candidates=np.stack([xx,yy],1);distance=np.linalg.norm(candidates-shoulder,axis=1)
        point=candidates[np.argsort(distance)[-12:]].mean(0)
        error=float(np.linalg.norm(point-shift-expected)/math.hypot(w,h));errors.append(error)
        points.append({'frame':i,'endpoint_px':point.tolist(),'torso_translation_px':shift.tolist(),'expected_px':expected.tolist(),'error_diagonal':error})
        thumb=Image.fromarray(rgb);d=ImageDraw.Draw(thumb)
        for p,color in ((point,'red'),(expected+shift,'lime')):d.ellipse((p[0]-5,p[1]-5,p[0]+5,p[1]+5),outline=color,width=2)
        sheet.paste(ImageOps.pad(thumb,(240,240)),((i%5)*240,(i//5)*260));draw.text(((i%5)*240+3,(i//5)*260+242),f'{i}: {error:.3f}',fill='black')
    sheet.save(run/'endpoint-review.jpg')
    return {'method':'skin endpoint extreme-distance heuristic, torso translation aligned; inspect endpoint-review.jpg; not independent pose annotation','points':points,'mean_error_diagonal':float(np.mean(errors)) if errors else None,'max_error_diagonal':max(errors) if errors else None,'gate_mean_le_0_12':bool(errors and np.mean(errors)<=.12)}

def main(root):
    root=Path(root);runs={p.name:p for p in root.iterdir() if (p/'evaluation.json').exists()};pairs=[]
    def add(a,b):
        if a in runs and b in runs:pairs.append(compare(runs[a],runs[b]))
    base='dev-synthetic-object__baseline__baseline__s42'
    for v,s in [('repeat',42),('baseline',123),('source-retained',42)]:add(base,f'dev-synthetic-object__baseline__{v}__s{s}')
    for v in ('reference-alternate','reference-neutral'):add('dev-synthetic-object__baseline__reference-control__s42',f'dev-synthetic-object__baseline__{v}__s42')
    add('dev-synthetic-motion__baseline__baseline__s42','dev-synthetic-motion__baseline__frozen-motion__s42')
    for case in ('dev-real-object','hold-synthetic-object','hold-synthetic-motion','hold-real-object','hold-real-motion'):
        add(f'{case}__baseline__baseline__s42',f'{case}__candidate__baseline__s42')
    add('dev-real-object__baseline__mask-coverage__s42','dev-real-object__candidate__mask-coverage__s42')
    resources=[];motion={}
    for name,run in runs.items():
        info=json.loads((run/'evaluation.json').read_text());samples=[]
        for line in (run/'gpu.csv').read_text().splitlines()[1:]:
            try:
                fields=line.split(',');samples.append([float(fields[-3]),float(fields[-2]),float(fields[-1])])
            except ValueError:pass
        record={'run':name,'worker_seconds':info['worker_elapsed_seconds'],'gpu_sample_count':len(samples)}
        if samples:
            arr=np.asarray(samples);record.update(peak_vram_MiB=float(arr[:,1].max()),mean_gpu_utilization_percent=float(arr[:,0].mean()),mean_power_W=float(arr[:,2].mean()))
        resources.append(record)
        m=motion_landmarks(run)
        if m:motion[name]=m
        # All frames, not just five time samples, for collapse inspection.
        images=frames(run);sheet=Image.new('RGB',(5*240,4*260),'white');d=ImageDraw.Draw(sheet)
        for i,img in enumerate(images):sheet.paste(ImageOps.pad(Image.fromarray(img),(240,240)),((i%5)*240,(i//5)*260));d.text(((i%5)*240+3,(i//5)*260+242),str(i),fill='black')
        sheet.save(run/'all-frames.jpg')
    result={'pairs':pairs,'resources':resources,'synthetic_motion':motion}
    (root.parent/'paired-analysis.json').write_text(json.dumps(result,indent=2));print(f'{len(pairs)} pairs, {len(resources)} resources, {len(motion)} endpoint records')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root');a=p.parse_args();main(a.root)
