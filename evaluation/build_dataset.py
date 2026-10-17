"""Deterministic eight-case dataset, with independently sourced live-action holdouts."""
import argparse,hashlib,json,math,shutil,subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from proof_inputs import create_fixture
from motion_inputs import draw_character

def command(args): subprocess.run(args,check=True,capture_output=True,timeout=90)
def encode(folder,target):
    command(['ffmpeg','-y','-loglevel','error','-framerate','8','-i',str(folder/'%04d.png'),'-frames:v','17','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(target)])
def rotate_metadata(normal,target):
    encoded=target.with_name('encoded.mp4')
    command(['ffmpeg','-y','-loglevel','error','-i',str(normal),'-vf','transpose=1','-c:v','libx264','-crf','18',str(encoded)])
    command(['ffmpeg','-y','-loglevel','error','-display_rotation','90','-i',str(encoded),'-c','copy',str(target)])
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height:stream_side_data=rotation','-of','json',str(target)]))
    stream=probe['streams'][0]
    if not any(abs(item.get('rotation',0))==90 for item in stream.get('side_data_list',[])):
        raise ValueError('Rotation test requires an actual display-matrix tag')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main(raw,output):
    raw,output=Path(raw).resolve(),Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    cases=[]
    for split in ('development','held-out'):
      for kind in ('synthetic-object','synthetic-motion','real-object','real-motion'):
        ident=('dev-' if split=='development' else 'hold-')+kind
        root=output/ident;root.mkdir(exist_ok=True)
        mode='object-swap' if kind.endswith('object') else 'motion-transfer'
        src=root/'frames';src.mkdir(exist_ok=True)
        ref=root/'reference.png';normal=root/'normal.mp4'
        bbox=[.15,.36,.35,.38];end=[.51,.36,.35,.38]
        rotated=False;source_record={'author':'montfortmini contributors','license':'MIT','source':'original procedural drawing'}
        notes=[];annotations={}
        if kind=='synthetic-object':
            create_fixture(root,width=320,height=320,frames=17)
            for i,file in enumerate(sorted((root/'source').glob('*.png'))):
                frame=Image.open(file).convert('RGB')
                if split=='held-out':
                    frame=ImageOps.mirror(frame)
                    arr=np.asarray(frame).copy();m=(arr[:,:,0]>100)&(arr[:,:,0]>arr[:,:,1]*1.5)
                    arr[m]=np.array([230,155,30]);frame=Image.fromarray(arr)
                frame.save(src/f'{i:04d}.png')
            if split=='held-out':
                bbox,end=[.14,.36,.35,.38],[.50,.36,.35,.38]
                bbox,end=end,bbox
                arr=np.asarray(Image.open(ref).convert('RGB')).copy()
                m=(arr[:,:,2]>arr[:,:,0]*1.3)&(arr[:,:,2]>arr[:,:,1]*1.15)
                arr[m]=[40,165,75];Image.fromarray(arr).save(ref)
            annotations['expected_centers']=[[.32+.36*i/16,.56] if split=='development' else [.68-.36*i/16,.56] for i in range(17)]
            annotations['target_color']='blue' if split=='development' else 'green'
            prompt=('A single smooth solid blue sphere moves from left to right on a gray floor. Fixed camera.' if split=='development' else 'A single smooth solid green sphere moves from right to left on a gray floor. Fixed camera.')
        elif kind=='synthetic-motion':
            for i in range(17):
                angle=-.9+2.2*i/16 if split=='development' else 1.1-1.6*i/16
                frame=draw_character(angle)
                if split=='held-out': frame=ImageOps.mirror(frame)
                frame.save(src/f'{i:04d}.png')
                elbow=(185+39*math.cos(angle),136-39*math.sin(angle))
                hand=(elbow[0]+29*math.cos(angle+.65),elbow[1]-29*math.sin(angle+.65))
                annotations.setdefault('moving_endpoint',[]).append([(320-hand[0] if split=='held-out' else hand[0])/320,hand[1]/320])
            reference=draw_character(-.9,blue=True)
            if split=='held-out':
                reference=ImageOps.mirror(reference);arr=np.asarray(reference).copy();m=(arr[:,:,2]>arr[:,:,0]*1.4)&(arr[:,:,2]>arr[:,:,1]*1.2);arr[m]=[157,63,191];reference=Image.fromarray(arr)
            reference.save(ref);bbox=end=[0,0,1,1]
            prompt=('An illustrated orange-haired character in a blue shirt follows the arm movement in the source clip. Full body, stable appearance.' if split=='development' else 'An illustrated orange-haired character in a purple shirt follows the lowering arm movement in the source clip. Full body, stable appearance.')
            annotations['target_color']='blue' if split=='development' else 'purple'
        else:
            name=('ball' if split=='development' else 'bounce') if kind=='real-object' else ('walk' if split=='development' else 'jacks')
            source_record=json.loads((raw/f'{name}.json').read_text())
            start={'ball':18.0,'bounce':4.0,'walk':15.8,'jacks':6.0}[name]
            command(['ffmpeg','-y','-loglevel','error','-ss',str(start),'-i',str(raw/f'{name}.webm'),'-vf','fps=8,scale=480:-2','-frames:v','17','-start_number','0',str(src/'%04d.png')])
            notes.append(f'Original recording {name}, start {start}s, 8fps, first 17 frames; resized to 480px long side.')
            if kind=='real-object':
                # Static boxes deliberately exercise the existing manual-region capability.
                bbox=end=([.32,.22,.40,.46] if split=='development' else [.21,.02,.32,.84])
                target='blue' if split=='development' else 'green'
                fixture=root/'reference-fixture';create_fixture(fixture)
                reference=Image.open(fixture/'reference.png').convert('RGB')
                if target=='green':
                    arr=np.asarray(reference).copy();m=(arr[:,:,2]>arr[:,:,0]*1.3)&(arr[:,:,2]>arr[:,:,1]*1.15);arr[m]=[40,165,75];reference=Image.fromarray(arr)
                reference.save(ref);annotations['target_color']=target
                prompt=f'Replace only the selected ball with a single smooth solid {target} sphere shown in the reference. Preserve its motion and natural lighting.'
                if split=='development': rotated=True;notes.append('Rotation-metadata robustness case: stored pixels transposed, display rotation restores original orientation.')
            else:
                reference=draw_character(-.9,blue=True)
                if split=='held-out':
                    arr=np.asarray(reference).copy();m=(arr[:,:,2]>arr[:,:,0]*1.4)&(arr[:,:,2]>arr[:,:,1]*1.2);arr[m]=[157,63,191];reference=Image.fromarray(arr)
                reference.save(ref);bbox=end=[0,0,1,1]
                annotations['target_color']='blue' if split=='development' else 'purple'
                prompt=('An illustrated orange-haired character in a blue shirt walks away with the same gait as the source person. Full body, fixed framing.' if split=='development' else 'An illustrated orange-haired character in a purple shirt performs the jumping jacks from the source clip. Full body, stable appearance.')
                if split=='held-out': rotated=True;notes.append('Held-out camera-metadata case, independent recording.')
                notes.append('Live-action driving clip to an illustrated reference: a cross-domain transfer test, not a photorealistic identity benchmark.')
        encode(src,normal)
        video=root/'input.mp4'
        if rotated: rotate_metadata(normal,video)
        else: shutil.copyfile(normal,video)
        (root/'source-provenance.json').write_text(json.dumps(source_record,indent=2))
        cases.append(dict(id=ident,split=split,kind=kind,mode=mode,video=f'{ident}/input.mp4',reference=f'{ident}/reference.png',
                          frames=17,prompt=prompt,bbox=bbox,end_bbox=end,rotation_metadata=rotated,annotations=annotations,notes=notes,
                          source_provenance=f'{ident}/source-provenance.json',sha256={'video':sha(video),'reference':sha(ref)}))
    manifest={'protocol':'PROTOCOL.md v1','dataset_revision':2,'cases':cases}
    (output/'dataset.json').write_text(json.dumps(manifest,indent=2))
    print('Frozen dataset:',output/'dataset.json')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--raw',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();main(args.raw,args.output)
