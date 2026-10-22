"""Transparent diagnostics; automated metrics never replace visual acceptance."""
import argparse,csv,hashlib,json,math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageOps

def read_video(path):
    capture=cv2.VideoCapture(str(path));frames=[]
    while True:
        ok,frame=capture.read()
        if not ok:break
        frames.append(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
    fps=capture.get(cv2.CAP_PROP_FPS);capture.release()
    return np.stack(frames),fps

def target_component(rgb,color,roi=None):
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    bands={'blue':(95,135),'green':(35,85),'purple':(125,170)}
    lo,hi=bands[color]
    mask=((hsv[:,:,0]>=lo)&(hsv[:,:,0]<=hi)&(hsv[:,:,1]>=80)&(hsv[:,:,2]>=45)).astype(np.uint8)
    if roi is not None:mask*=roi.astype(np.uint8)
    count,labels,stats,centers=cv2.connectedComponentsWithStats(mask,8)
    if count<2:return None
    best=1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA]));area=int(stats[best,cv2.CC_STAT_AREA])
    if area<rgb.shape[0]*rgb.shape[1]*.0003:return None
    contours,_=cv2.findContours((labels==best).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contour=max(contours,key=cv2.contourArea);perimeter=cv2.arcLength(contour,True)
    return {'center':centers[best].tolist(),'area':area,'circularity':float(4*math.pi*cv2.contourArea(contour)/(perimeter**2)) if perimeter else 0}

def analyze(run):
    info=json.loads((run/'evaluation.json').read_text());case=info['case'];n=case['frames']
    source=np.stack([np.asarray(Image.open(run/'inputs/source'/f'{i:04d}.png').convert('RGB')) for i in range(n)])
    masks=np.stack([np.asarray(Image.open(run/'inputs/masks'/f'{i:04d}.png').convert('L'))>0 for i in range(n)])
    raw=np.stack([np.asarray(Image.open(run/'raw'/f'{i:04d}.png').convert('RGB')) for i in range(n)])
    composite=np.stack([np.asarray(Image.open(run/'composite'/f'{i:04d}.png').convert('RGB')) for i in range(n)])
    height,width=source.shape[1:3];outside=~masks
    decoded,fps=read_video(run/'composite.mp4')
    eroded_outside=np.stack([~cv2.dilate(mask.astype(np.uint8),np.ones((17,17),np.uint8)).astype(bool) for mask in masks])
    def errors(images,region):
        values=np.abs(images.astype(np.float32)-source.astype(np.float32))[region].ravel()
        return {'mae_255':float(values.mean()),'p95_255':float(np.percentile(values,95)),'max_255':float(values.max())} if values.size else None
    png_error=errors(composite,outside)
    raw_error=errors(raw,eroded_outside)
    video_error=errors(decoded,eroded_outside) if decoded.shape==source.shape else None
    target=[];motion_errors=[];circles=[];temporal=[]
    expected=case.get('annotations',{}).get('expected_centers',[])
    for i,image in enumerate(raw):
        found=target_component(image,case['annotations']['target_color'],masks[i] if case['mode']=='object-swap' else None)
        target.append(found)
        if found:
            circles.append(found['circularity'])
            if i<len(expected) and expected[i] is not None:
                ex,ey=expected[i];motion_errors.append(float(np.linalg.norm(np.asarray(found['center'])-[ex*width,ey*height])/math.hypot(width,height)))
        if i:
            prev=cv2.cvtColor(source[i-1],cv2.COLOR_RGB2GRAY);now=cv2.cvtColor(source[i],cv2.COLOR_RGB2GRAY)
            flow=cv2.calcOpticalFlowFarneback(prev,now,None,.5,3,15,3,5,1.2,0)
            x,y=np.meshgrid(np.arange(width,dtype=np.float32),np.arange(height,dtype=np.float32))
            warped=cv2.remap(image.astype(np.float32),x+flow[:,:,0],y+flow[:,:,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
            region=masks[i]|masks[i-1]
            temporal.append(float(np.abs(warped-raw[i-1].astype(np.float32))[region].mean()/255))
    record={'run':run.name,'case':case['id'],'split':case['split'],'mode':case['mode'],'profile':info['profile'],'variant':info['variant'],
            'seed':info['seed'],'worker_seconds':info['worker_elapsed_seconds'],'frames':len(raw),'width':width,'height':height,
            'technical_frames_pass':len(raw)==n and decoded.shape==source.shape and abs(fps-8)<.01,
            'target_color_presence_fraction':sum(x is not None for x in target)/n,
            'target_circularity_median':float(np.median(circles)) if circles else None,
            'object_centroid_mean_error_diagonal':float(np.mean(motion_errors)) if motion_errors else None,
            'composite_png_outside_mask':png_error,'raw_outside_dilated_mask':raw_error,'mp4_outside_dilated_mask':video_error,
            'source_flow_aligned_temporal_residual_mean':float(np.mean(temporal)),
            'manual_review_required':True,'overall_pass':None,
            'metric_caveats':['Color presence is not identity or silhouette fidelity.','Source-flow residual is confounded by intended appearance changes and is diagnostic only.','No automatic pass without the registered visual gates.']}
    (run/'metrics.json').write_text(json.dumps(record,indent=2))
    (run/'frame-diagnostics.json').write_text(json.dumps({'target_components':target,'flow_aligned_residuals':temporal},indent=2))
    # Five time samples, with original reference, input, raw and composite together.
    samples=[0,4,8,12,16];sheet=Image.new('RGB',(1120,1520),'#eeeeee');draw=ImageDraw.Draw(sheet)
    ref=Image.open(run/'inputs/reference.png').convert('RGB')
    for col,label in enumerate(('Reference','Prepared source','Raw model','Composite')):draw.text((col*280+8,8),label,fill='black')
    for row,i in enumerate(samples):
        for col,img in enumerate((ref,Image.fromarray(source[i]),Image.fromarray(raw[i]),Image.fromarray(composite[i]))):
            thumb=ImageOps.pad(img,(280,280),color='#dddddd');sheet.paste(thumb,(col*280,row*300+30))
        draw.text((8,row*300+312),f'frame {i}',fill='black')
    sheet.save(run/'review-sheet.jpg')
    return record

def main(root):
    root=Path(root);records=[]
    for run in sorted(root.iterdir()):
        if run.is_dir() and (run/'evaluation.json').exists():
            record=analyze(run);records.append(record);print(record['run'],round(record['worker_seconds'],2),round(record['target_color_presence_fraction'],2),flush=True)
    (root.parent/'metrics.json').write_text(json.dumps(records,indent=2))
    columns=['run','split','mode','profile','variant','seed','worker_seconds','target_color_presence_fraction','target_circularity_median','object_centroid_mean_error_diagonal','source_flow_aligned_temporal_residual_mean']
    with (root.parent/'metrics.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(records)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('root');args=parser.parse_args();main(args.root)
