"""Build an offline, label-blinded review packet and a separate unblinding key."""
import argparse,csv,hashlib,html,json,random,shutil,zipfile
from pathlib import Path

def main(root):
    root=Path(root).resolve();packet=root/'blind-review';packet.mkdir(exist_ok=True)
    runs=[p for p in sorted((root/'runs').iterdir()) if (p/'evaluation.json').exists()]
    random.Random(20261017).shuffle(runs);key=[];rows=[];cards=[]
    for i,run in enumerate(runs,1):
        ident=f'sample-{i:02d}';folder=packet/ident;folder.mkdir(exist_ok=True)
        for source,name in [(run/'source.mp4','source.mp4'),(run/'generated.mp4','raw.mp4'),(run/'composite.mp4','composite.mp4'),(run/'inputs/reference.png','reference.png')]:shutil.copyfile(source,folder/name)
        key.append({'sample':ident,'run':run.name,'evaluation_sha256':hashlib.sha256((run/'evaluation.json').read_bytes()).hexdigest()})
        for stage in ('raw','composite'):
            rows.append({'sample':ident,'stage':stage,'reviewer':'','fidelity_0_4':'','motion_0_4':'','stability_0_4':'','acceptable_subject_frames_of_17':'','catastrophic_failure_frames':'','notes':''})
        videos=''.join(f'<div><b>{label}</b><video controls loop muted src="{ident}/{file}.mp4"></video></div>' for label,file in [('Original prepared driving clip','source'),('Raw model output','raw'),('Composited output','composite')])
        cards.append(f'<article><h2>{ident}</h2><div class="row"><div><b>Submitted reference</b><img src="{ident}/reference.png"></div>{videos}</div></article>')
    (root/'unblinding-key.json').write_text(json.dumps(key,indent=2))
    with (packet/'review.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    rubric='''Review every frame at normal speed and frame by frame. Score raw and composited outputs separately. Fidelity: 0 wrong/absent, 1 weak, 2 mixed, 3 clear with minor defects, 4 consistent. Use the same scale for recognizable source motion and stability. Record collapse, duplication and disappearance frames. Gates: each score >=3, >=14/17 acceptable subject frames, no catastrophic collapse; motion/background numerical gates are checked separately. The original driving clip is shown even for temporal-control interventions; reveal intervention labels only after scoring. These are short, mixed synthetic/real tests, not a population sample. Do not infer a system success rate without the separate validity notes and key. No independent review has yet occurred.'''
    (packet/'README.txt').write_text(rubric+'\nOpen index.html in a browser. Fill review.csv before opening ../unblinding-key.json. Footage licensing is recorded under ../data/*/source-provenance.json and original-recordings.\n')
    (packet/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Blinded video review</title><style>body{font:16px sans-serif;margin:24px;background:#eee}article{background:white;padding:16px;margin:24px 0}.row{display:flex;gap:12px;flex-wrap:wrap}.row div{width:22%;min-width:220px}img,video{display:block;width:100%;max-height:360px;object-fit:contain}</style><h1>Blinded video review</h1><p>'+html.escape(rubric)+'</p>'+''.join(cards))
    entries=[]
    for file in sorted(root.rglob('*')):
        if file.is_file() and file.name not in ('evidence-inventory.json','montfortmini-validation.zip','genjutsu-queued.jpg'):
            entries.append({'path':file.relative_to(root).as_posix(),'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'included_in_bundle':file.name!='evidence.zip'})
    (root/'evidence-inventory.json').write_text(json.dumps(entries,indent=2))
    target=root.parent/'montfortmini-validation.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for item in entries:
            if Path(item['path']).name=='evidence.zip':continue # expanded originals already included
            z.write(root/item['path'],'montfortmini-validation/'+item['path'])
        z.write(root/'evidence-inventory.json','montfortmini-validation/evidence-inventory.json')
    print(f'{len(runs)} blinded samples; {target.stat().st_size} archive bytes')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root');a=p.parse_args();main(a.root)
