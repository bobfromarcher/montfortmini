"""Source-anchored all-frame color diagnostics; never a substitute for visual gates.

No region is selected from generated colors. Reuse before reviewing new output.
"""
import argparse
import csv
import io
import json
from pathlib import Path
import zipfile
import cv2
import numpy as np
from PIL import Image


def pixel_stats(rgb, region, reference_chromaticity):
    pixels = np.asarray(rgb)[region].astype(np.float64)
    if not len(pixels): raise ValueError('Empty diagnostic region')
    median = np.median(pixels, axis=0)
    chroma = median / max(float(median.sum()), 1e-12)
    luma = pixels @ np.array([.2126, .7152, .0722]) / 255
    # HSV here is diagnostic only; it never chooses which output pixels count.
    hsv = cv2.cvtColor(np.asarray(rgb, dtype=np.uint8), cv2.COLOR_RGB2HSV)
    return dict(pixels=int(len(pixels)), median_rgb_255=median.tolist(),
                chromaticity_rgb_sum1=chroma.tolist(),
                chromaticity_distance=float(np.linalg.norm(chroma-reference_chromaticity)),
                encoded_luma_p10_median_p90=np.percentile(luma, [10,50,90]).tolist(),
                median_saturation_255=float(np.median(hsv[...,1][region])))


def summarize(rows):
    medians=np.array([r['median_rgb_255'] for r in rows])
    chroma=np.array([r['chromaticity_rgb_sum1'] for r in rows])
    return dict(frames=len(rows),
                median_chromaticity_distance=float(np.median([r['chromaticity_distance'] for r in rows])),
                median_encoded_luma=float(np.median([r['encoded_luma_p10_median_p90'][1] for r in rows])),
                median_saturation_255=float(np.median([r['median_saturation_255'] for r in rows])),
                median_adjacent_rgb_step_255=float(np.median(np.linalg.norm(np.diff(medians,axis=0),axis=1))),
                max_adjacent_rgb_step_255=float(np.max(np.linalg.norm(np.diff(medians,axis=0),axis=1))),
                median_adjacent_chromaticity_step=float(np.median(np.linalg.norm(np.diff(chroma,axis=0),axis=1))))


def analyze(archive_path, cases):
    kernel=np.ones((5,5),np.uint8)  # frozen2px inward erosion
    with zipfile.ZipFile(archive_path) as z:
        def read(n, mode): return np.asarray(Image.open(io.BytesIO(z.read(n))).convert(mode))
        fg=np.stack([read(f'foreground/{i:04d}.png','L')>0 for i in range(17)])
        core=np.stack([cv2.erode(m.astype(np.uint8),kernel)>0 for m in fg])
        ref_mask=cv2.erode((read('reference-foreground.png','L')>0).astype(np.uint8),kernel)>0
        ref=read('reference.png','RGB')
        med=np.median(ref[ref_mask],axis=0);ref_chroma=med/med.sum()
        source=np.stack([read(f'source/{i:04d}.png','RGB') for i in range(17)])
    result=dict(method='Median RGB, encoded luma quantiles, HSV saturation, RGB/sum chromaticity distance; all17 frames. Fixed original source foreground eroded2px, original reference foreground eroded2px. No generated-color thresholding.',
                reference=pixel_stats(ref,ref_mask,ref_chroma),
                source_core_areas=[int(m.sum()) for m in core],
                source_trajectory_stats=[pixel_stats(source[i],core[i],ref_chroma) for i in range(17)],
                cases={},
                limits='One seed/recording; frames are correlated, not independent trials. Source masks can include background if generated geometry drifts. Color statistics can improve on a missing/wrong object and cannot override presence/shape/motion/material gates. Different lighting/materials confound reference distances. Encoded RGB luma is not linear-light reflectance. Adjacent-frame changes include source motion/illumination; no claim of motion-compensated flicker or statistical significance.')
    for label,root in cases.items():
        result['cases'][label]={}
        for stage in ('raw','composite'):
            frames=[np.asarray(Image.open(root/stage/f'{i:04d}.png').convert('RGB')) for i in range(17)]
            rows=[dict(frame=i,**pixel_stats(rgb,core[i],ref_chroma)) for i,rgb in enumerate(frames)]
            result['cases'][label][stage]=dict(summary=summarize(rows),rows=rows)
    labels=list(cases)
    if len(labels)==2:
        a,b=labels;result['paired']={}
        for stage in ('raw','composite'):
            old=result['cases'][a][stage];new=result['cases'][b][stage]
            changes=[dict(frame=i,chromaticity_distance_delta=n['chromaticity_distance']-o['chromaticity_distance'],
                          median_luma_delta=n['encoded_luma_p10_median_p90'][1]-o['encoded_luma_p10_median_p90'][1],
                          saturation_delta=n['median_saturation_255']-o['median_saturation_255'])
                     for i,(o,n) in enumerate(zip(old['rows'],new['rows']))]
            result['paired'][stage]=dict(baseline=a,candidate=b,rows=changes,
                frames_chromaticity_closer=sum(r['chromaticity_distance_delta']<0 for r in changes),
                median_chromaticity_distance_delta=float(np.median([r['chromaticity_distance_delta'] for r in changes])))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    result=analyze(args.inputs,dict(baseline=args.baseline,candidate=args.candidate))
    args.output.write_text(json.dumps(result,indent=2),encoding='utf-8')
    with args.output.with_suffix('.csv').open('w',newline='',encoding='utf-8') as f:
        fields=['case','stage','frame','pixels','median_r','median_g','median_b','chromaticity_distance','median_luma','saturation']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for case,stages in result['cases'].items():
            for stage,record in stages.items():
                for r in record['rows']:
                    w.writerow(dict(case=case,stage=stage,frame=r['frame'],pixels=r['pixels'],median_r=r['median_rgb_255'][0],median_g=r['median_rgb_255'][1],median_b=r['median_rgb_255'][2],chromaticity_distance=r['chromaticity_distance'],median_luma=r['encoded_luma_p10_median_p90'][1],saturation=r['median_saturation_255']))
    print(json.dumps({k:v['summary'] for k,v in result['cases']['candidate'].items()},indent=2))


if __name__=='__main__': main()
