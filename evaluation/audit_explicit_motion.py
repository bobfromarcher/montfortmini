"""Technical paired audit and full-frame review sheets; never assigns visual pass."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw


def audit(control,candidate,output):
    output.mkdir(parents=True,exist_ok=False)
    old=np.load(control/'inputs/conditioning.npz',allow_pickle=False)
    new=np.load(candidate/'inputs/conditioning.npz',allow_pickle=False)
    paired={key:bool(np.array_equal(old[key],new[key])) for key in ('source','mask','reference')}
    raw=sorted((candidate/'raw').glob('*.png'))
    same=all(np.array_equal(np.asarray(Image.open(p)),np.asarray(Image.open(candidate/'composite'/p.name))) for p in raw)
    for start in range(0,len(raw),3):
        sheet=Image.new('RGB',(1440,3*586),'white');d=ImageDraw.Draw(sheet)
        for row,i in enumerate(range(start,min(start+3,len(raw)))):
            for col,(label,path) in enumerate((('Source',candidate/'inputs/source'),('Retained Animate2 control',control/'raw'),('Explicit-pose candidate',candidate/'raw'))):
                im=Image.open(path/f'{i:04d}.png').convert('RGB')
                if im.size!=(480,560):raise ValueError('Unexpected actual resolution')
                sheet.paste(im,(col*480,row*586+26));d.text((col*480+8,row*586+6),f'{label} frame{i:02d}',fill='black')
        sheet.save(output/f'comparison-{start:02d}.jpg',quality=94)
    graph=json.loads((candidate/'workflow-api.json').read_text())
    prior=json.loads((control/'workflow-api.json').read_text())
    changed=[k for k in sorted(set(graph)|set(prior)) if graph.get(k)!=prior.get(k)]
    resource=list(csv.DictReader((candidate/'candidate-gpu.csv').open()))
    record=json.loads((candidate/'candidate.json').read_text())
    result={'status':'technical-audit-only','paired_conditioning_tensors':paired,
            'actual_raw_frames':len(raw),'raw_composite_png_exact_equal':same,
            'raw_sizes':sorted(set(Image.open(p).size for p in raw)),
            'changed_graph_nodes':changed,'new_control_shape':{k:list(new[k].shape) for k in ('pose','face')},
            'worker_elapsed_seconds':record['worker_elapsed_seconds'],
            'sampled_peak_vram_MiB':max((float(x['memory_MiB']) for x in resource),default=None),
            'resource_sample_count':len(resource),
            'raw_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in raw},
            'limits':'Model+conditioning+solver bundle changed deliberately. Paired inputs do not isolate a single component. Full motion mask means no outside-preservation assertion. Agent visual and normal-speed review required; independent professional scoring pending.'}
    (output/'technical-audit.json').write_text(json.dumps(result,indent=2))
    if not all(paired.values()) or len(raw)!=33 or not same:raise ValueError('Technical pairing gate failed')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('control','candidate','output'):parser.add_argument('--'+name,type=Path,required=True)
    a=parser.parse_args();audit(a.control,a.candidate,a.output)
