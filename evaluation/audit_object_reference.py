"""Offline paired reference experiment audit. Acceptance also needs visual review.

python evaluation/audit_object_reference.py evaluation/object-reference
"""
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

import cv2
import numpy as np
from PIL import Image
from quality_analysis import component,error,images,video


def audit(root,contrast='reference'):
    read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
    frozen=read(root/'freeze.json');record=read(root/'candidate.json')
    runtime=read(root/'object-runtime.json')
    baseline=Path(__file__).parent/'quality/samples/new-real-object__candidate__s42'
    with zipfile.ZipFile(root/'inputs.zip') as archive:
        source=np.stack([np.asarray(Image.open(io.BytesIO(archive.read(f'source/{i:04d}.png'))).convert('RGB')) for i in range(17)])
        masks=np.stack([np.asarray(Image.open(io.BytesIO(archive.read(f'masks/{i:04d}.png'))).convert('L'))>0 for i in range(17)])
        added={n for n in archive.namelist() if not (baseline/'inputs'/n).is_file()}
        changed=[n for n in archive.namelist() if n not in added and archive.read(n)!=(baseline/'inputs'/n).read_bytes()]
        old=np.load(baseline/'inputs/conditioning.npz');new=np.load(io.BytesIO(archive.read('conditioning.npz')))
        tensor_same={k:bool(np.array_equal(old[k],new[k])) for k in old.files}
        reference=np.asarray(Image.open(io.BytesIO(archive.read('reference.png'))).convert('RGB'),dtype=np.float32)/255
        if new['reference'].ndim==4:reference=reference[None]
        ref_tensor_matches=bool(np.array_equal(reference,new['reference']))
    raw=images(root/'raw');comp=images(root/'composite');encoded,fps=video(root/'composite.mp4')
    dilated=np.stack([cv2.dilate(m.astype('uint8'),np.ones((17,17),np.uint8))>0 for m in masks])
    rows=[]
    for i in range(17):
        src=component(source[i],'yellow',masks[i]);green=component(raw[i],'green',dilated[i])
        finished=component(comp[i],'green',masks[i])
        rows.append({'frame':i,'source_yellow':src,'raw_green':green,'composite_green':finished,
                     'raw_yellow':component(raw[i],'yellow',dilated[i]),
                     'area_ratio':green['area']/src['area'] if src and green else None,
                     'centroid_error_diagonal':float(np.linalg.norm(np.asarray(green['center'])-src['center'])/np.hypot(480,272)) if src and green else None})
    expected_graph=read(baseline/'workflow-api.json')
    is_luminance=contrast in ('luminance','luminance-prompt','reference-luma','reference-chroma','color-prompt')
    if contrast in ('prompt','luminance-prompt'):expected_graph['4']['inputs']['text']=read(root/'mask-annotation.json')['after']
    if is_luminance:expected_graph['6']['class_type']='OpenJutsuLuminanceInputs'
    if contrast=='reference-luma':
        expected_graph=read(root.parent/'object-luminance-prompt/workflow-api.json')
        expected_graph['6']['class_type']='OpenJutsuReferenceLumaInputs'
    if contrast=='reference-chroma':
        expected_graph=read(root.parent/'object-reference-luma/workflow-api.json')
        expected_graph['6']['class_type']='OpenJutsuReferenceChromaInputs'
    if contrast=='color-prompt':
        expected_graph=read(root.parent/'object-reference-chroma/workflow-api.json')
        expected_graph['4']['inputs']['text']=read(root/'prompt-annotation.json')['after']
    archive_changes={'reference':{'reference.png','conditioning.npz'},'prompt':set(),'luminance':{'conditioning.npz'},'luminance-prompt':{'conditioning.npz'},'reference-luma':{'conditioning.npz'},'reference-chroma':{'conditioning.npz'},'color-prompt':{'conditioning.npz'}}[contrast]
    checks={'technical_success':record['status']=='succeeded',
            'paired_archive_changes_exact':set(changed)==archive_changes,
            'conditioning_change_exact':tensor_same=={'source':not is_luminance,'mask':True,'reference':contrast!='reference'},
            'reference_tensor_matches_png':ref_tensor_matches,
            'paired_graph_changes_exact':read(root/'workflow-api.json')==expected_graph,
            'worker_input_matches_freeze':record['input_archive_sha256']==frozen['artifact_sha256']['inputs.zip'],
            'frozen_inputs_exact':all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen['artifact_sha256'].items()),
            'runtime_source_matches_freeze':runtime['source_sha256']==frozen['source_sha256'],
            'size_frames_fps':raw.shape==source.shape==comp.shape==encoded.shape==(17,272,480,3) and fps==8}
    expected_additions=({'reference-foreground.png'}|{f'foreground/{i:04d}.png' for i in range(17)}) if contrast in ('reference-luma','reference-chroma','color-prompt') else set()
    checks['only_expected_annotation_entries_added']=added==expected_additions
    if is_luminance:
        with np.load(root/'inputs/runtime-conditioning.npz') as actual:
            source_delta=float(np.abs(actual['source']-new['source']).max())
            checks['executed_node_tensors_match_prepared']=all(np.array_equal(actual[k],new[k]) for k in ('mask','reference')) and source_delta<=(2e-7 if contrast in ('reference-luma','reference-chroma','color-prompt') else 0)
            rgb=source.astype(np.float32)/255
            luma=(rgb*np.asarray([.2126,.7152,.0722],dtype=np.float32)).sum(axis=-1,keepdims=True)
            expected=np.where(masks[...,None],luma,rgb)
            if contrast in ('reference-luma','reference-chroma','color-prompt'):
                sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
                from object_reference_luma_inputs import reference_luma_control
                with zipfile.ZipFile(root/'inputs.zip') as z:
                    fg=np.stack([np.asarray(Image.open(io.BytesIO(z.read(f'foreground/{i:04d}.png'))).convert('L'),dtype=np.float32)/255 for i in range(17)])
                    ref_fg=np.asarray(Image.open(io.BytesIO(z.read('reference-foreground.png'))).convert('L'))>0
                if contrast in ('reference-chroma','color-prompt'):
                    from object_reference_chroma_inputs import reference_chroma_control
                    expected,normalization=reference_chroma_control(rgb,masks.astype(np.float32),reference,fg,ref_fg)
                    actual_record=read(root/'inputs/runtime-chroma-normalization.json')
                    checks['chroma_preserves_prior_luma_without_clipping']=normalization['luma_delta_vs_prior_max']<=2e-7 and normalization['clipped_values']==0
                    checks['executed_chromaticity_matches']=np.allclose(actual_record['reference_rgb_per_unit_luma'],normalization['reference_rgb_per_unit_luma'],rtol=0,atol=2e-7)
                    checks['container_preflight_passed']=read(root/'container-preflight.json')['ok'] is True
                    if contrast=='color-prompt':
                        checks['input_archive_byte_exact_vs_chroma']=(root/'inputs.zip').read_bytes()==(root.parent/'object-reference-chroma/inputs.zip').read_bytes()
                        annotation=read(root/'prompt-annotation.json')
                        checks['only_two_green_words_removed']=annotation['before'].count(' green')==2 and annotation['after']==annotation['before'].replace(' green','')
                        checks['frozen_analysis_sources_match']=all(hashlib.sha256((Path(__file__).resolve().parents[1]/n).read_bytes()).hexdigest()==h for n,h in frozen['analysis_sha256'].items())
                    else:
                        with zipfile.ZipFile(root.parent/'object-reference-luma/inputs.zip') as prior, zipfile.ZipFile(root/'inputs.zip') as current:
                            checks['chroma_only_input_contrast']=set(prior.namelist())==set(current.namelist()) and [n for n in prior.namelist() if prior.read(n)!=current.read(n)]==['conditioning.npz']
                else:
                    expected,normalization=reference_luma_control(rgb,masks.astype(np.float32),reference,fg,ref_fg)
                    actual_record=read(root/'inputs/runtime-luma-normalization.json')
                checks['executed_normalization_gain_matches']=abs(actual_record['gain']-normalization['gain'])<=1e-7
                checks['executed_control_matches_source_derived_chroma' if contrast in ('reference-chroma','color-prompt') else 'executed_control_matches_original_source_luma']=bool(np.allclose(actual['source'],expected,rtol=0,atol=2e-7))
            else:
                checks['executed_control_matches_original_source_luma']=bool(np.array_equal(actual['source'],expected))
            checks['outside_control_rgb_exact']=bool(np.array_equal(actual['source'][~masks],rgb[~masks]))
        if contrast=='luminance-prompt':
            with zipfile.ZipFile(root.parent/'object-luminance/inputs.zip') as other,zipfile.ZipFile(root/'inputs.zip') as current:
                checks['input_entries_exact_vs_luma_only']=all(other.read(n)==current.read(n) for n in current.namelist())
            paired_graph=read(root.parent/'object-luminance/workflow-api.json')
            paired_graph['4']['inputs']['text']=read(root/'mask-annotation.json')['after']
            checks['prompt_only_graph_contrast_vs_luma_only']=read(root/'workflow-api.json')==paired_graph
    with zipfile.ZipFile(root/'executed-source.zip') as archive:
        checks['source_snapshot_matches_freeze']=all(hashlib.sha256(archive.read(n)).hexdigest()==h for n,h in frozen['source_sha256'].items())
    green=sum(r['raw_green'] is not None for r in rows)
    ratios=[r['area_ratio'] for r in rows if r['area_ratio'] is not None]
    distances=[r['centroid_error_diagonal'] for r in rows if r['centroid_error_diagonal'] is not None]
    ratio=float(np.median(ratios)) if ratios else None
    distance=float(np.mean(distances)) if distances else None
    preservation=error(source,raw,~dilated);encoded_preservation=error(source,encoded,~dilated)
    composite_preservation=error(source,comp,~masks)
    gates={'reference_color':green>=15,'scale_proxy':ratio is not None and .8<=ratio<=1.25,
           'centroid':distance is not None and distance<=.1,
           'raw_preservation':preservation['mae_255']<=3 and preservation['p95_255']<=10,
           'encoded_preservation':encoded_preservation['mae_255']<=3 and encoded_preservation['p95_255']<=10,
           'composite_preservation':composite_preservation['max_255']==0}
    return {'contrast':contrast,'invariants_pass':all(checks.values()),'checks':checks,'diagnostic_gates':gates,
            'prepared_vs_executed_control_max_delta':source_delta if is_luminance else None,
            'diagnostic_gates_pass':all(gates.values()),'raw_green_reference_frames':green,
            'composite_green_reference_frames':sum(r['composite_green'] is not None for r in rows),
            'median_area_ratio':ratio,'mean_centroid_error_diagonal':distance,
            'raw_preservation':preservation,'encoded_preservation':encoded_preservation,
            'composite_preservation':composite_preservation,'rows':rows,
            'limits':'Known development footage. Color/area heuristics cannot certify reference likeness, motion or plausible scene lighting. Agent visual scores and independent review remain separate.'}


if __name__=='__main__':
    contrast='color-prompt' if '--color-prompt' in sys.argv else 'reference-chroma' if '--reference-chroma' in sys.argv else 'reference-luma' if '--reference-luma' in sys.argv else 'luminance-prompt' if '--luminance-prompt' in sys.argv else 'luminance' if '--luminance' in sys.argv else 'prompt' if '--prompt-only' in sys.argv else 'reference'
    result=audit(Path(sys.argv[1]),contrast);print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['invariants_pass'] and result['diagnostic_gates_pass'] else 1)
