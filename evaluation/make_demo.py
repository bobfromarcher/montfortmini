"""Build a captioned 108-second demo from retained original procedural results.

No generated frame is repaired, interpolated, or replaced. Video examples loop
at their original rate. Fonts are system-installed and are not redistributed.
"""
import argparse,hashlib,json,subprocess,textwrap
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps

SIZE=(1280,720);BG='#101116';FG='#efeff4';MUTED='#b3b6c6';ACCENT='#b7a0ff'


def font(size):
    for p in ['C:/Windows/Fonts/segoeui.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if Path(p).exists():return ImageFont.truetype(p,size)
    return ImageFont.load_default(size=size)


def text(d,xy,value,size=25,width=85,fill=FG,spacing=9):
    lines=[]
    for paragraph in value.split('\n'):lines.extend(textwrap.wrap(paragraph,width=width) or [''])
    d.multiline_text(xy,'\n'.join(lines),font=font(size),fill=fill,spacing=spacing)


def base(title,subtitle=''):
    im=Image.new('RGB',SIZE,BG);d=ImageDraw.Draw(im)
    text(d,(42,25),'montfortmini  /  Open Source Higgsfield',18,fill=ACCENT)
    text(d,(42,70),title,37,width=61)
    if subtitle:text(d,(42,130),subtitle,22,width=96,fill=MUTED)
    d.line((42,674,1238,674),fill='#343542',width=2)
    text(d,(42,686),'Recorded evidence • experimental • no Genjutsu-parity claim',16,fill=MUTED)
    return im


def encode_still(path,duration,out):
    subprocess.run(['ffmpeg','-y','-loglevel','error','-loop','1','-framerate','24','-i',str(path),'-t',str(duration),'-an','-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p',str(out)],check=True,timeout=180)


def main(samples,ui,output):
    samples=Path(samples);output=Path(output);output.mkdir(parents=True,exist_ok=True);assets=output/'demo-assets';assets.mkdir(exist_ok=True)
    segments=[];provenance=[]
    quality=samples.parent/'quality/samples'
    specs=[('object',quality/'new-synthetic-object__candidate__s42'),('motion',quality/'new-synthetic-motion__candidate__s42'),('failure',samples/'hold-synthetic-motion__candidate__baseline__s42')]
    intro=base('Two open video workflows','Reference-guided object replacement and character motion transfer.')
    d=ImageDraw.Draw(intro);text(d,(72,245),'A working prototype with real inference results.\nThis demo shows successes, a retained failure, and how to inspect the evidence.',33,width=62)
    text(d,(72,515),'MIT app code • pinned Comfy workflows • open weights',25,fill=ACCENT)
    intro.save(assets/'00.png');encode_still(assets/'00.png',8,assets/'00.mp4');segments.append(assets/'00.mp4')
    interface=base('Use the existing workbench','Clean-checkout interface; the preview is a labeled recorded example.')
    if ui and Path(ui).exists():
        image=Image.open(ui).convert('RGB');interface.paste(ImageOps.contain(image,(885,500)),(42,171));provenance.append({'asset':'workbench screenshot','sha256':hashlib.sha256(Path(ui).read_bytes()).hexdigest(),'rights':'Original app interface and original procedural example'})
        image.save(assets/'workbench.png')
    d=ImageDraw.Draw(interface);text(d,(957,208),'Upload video\nand one reference.\n\nDraw an object region, or choose motion.\n\nDownload MP4, graph and run details.',24,width=20)
    interface.save(assets/'01.png');encode_still(assets/'01.png',12,assets/'01.mp4');segments.append(assets/'01.mp4')
    for index,(kind,run) in enumerate(specs,2):
        name=run.name;title={'object':'Object replacement — frozen vertical test','motion':'Motion transfer — frozen two-arm test','failure':'Retained failure — lowering-arm test'}[kind]
        subtitle={'object':'Wan2.1 VACE 1.3B • seed 42 • new original synthetic test','motion':'Wan Animate2 distilled int8 • seed 42 • new original synthetic test','failure':'Extra arm and incomplete source motion. This case fails the quality gate.'}[kind]
        im=base(title,subtitle);d=ImageDraw.Draw(im)
        for col,label in enumerate(['Reference','Source','Raw model output','Finished']):text(d,(45+col*306,202),label,22)
        im.paste(ImageOps.pad(Image.open(run/'reference.png' if (run/'reference.png').exists() else run/'inputs/reference.png').convert('RGB'),(280,300),color='#292b33'),(45,245))
        text(d,(45,579),'Examples loop at the original 8fps. No interpolation or frame repair.',23,width=90)
        text(d,(45,619),'Finished object-background preservation comes from compositing.' if kind=='object' else 'Full-frame motion generation can change backgrounds and anatomy.',21,width=94,fill=MUTED)
        frame=assets/f'{index:02d}.png';im.save(frame)
        command=['ffmpeg','-y','-loglevel','error','-loop','1','-framerate','24','-i',str(frame)]
        for filename in ['source.mp4','generated.mp4','composite.mp4']:command+=['-stream_loop','-1','-i',str(run/filename)]
        filters=[];last='0:v'
        for j in range(1,4):
            filters.append(f'[{j}:v]scale=280:300:force_original_aspect_ratio=decrease,pad=280:300:(ow-iw)/2:(oh-ih)/2:color=0x292b33,fps=24[v{j}]')
            filters.append(f'[{last}][v{j}]overlay={45+j*306}:245[out{j}]');last=f'out{j}'
        movie=assets/f'{index:02d}.mp4';command+=['-filter_complex',';'.join(filters),'-map',f'[{last}]','-t','16','-an','-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p',str(movie)]
        subprocess.run(command,check=True,timeout=240);segments.append(movie)
        for filename in ['source.mp4','generated.mp4','composite.mp4','manifest.json','workflow-api.json']:
            path=run/filename
            if path.exists():provenance.append({'case':name,'file':filename,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rights':'Original MIT procedural fixtures; model output retains upstream model terms'})
    architecture=base('How it runs','Actual inference path; no Higgsfield backend calls.')
    d=ImageDraw.Draw(architecture)
    labels=['Workbench','Official\nComfy SDK','Self-hosted\nAPI proxy','Pinned\nComfyUI graph','Wan\nopen weights']
    for i,label in enumerate(labels):
        x=42+i*242;d.rounded_rectangle((x,245,x+215,367),radius=12,fill='#282a36',outline=ACCENT,width=2);text(d,(x+15,266),label,25,width=13)
        if i<4:text(d,(x+221,285),'→',22,fill=ACCENT)
    text(d,(55,424),'Modal L40S for the recorded runs; one GPU worker at a time.\nLocal NVIDIA Docker instructions are provided; GPU Docker reproduction is still pending.',27,width=79)
    architecture.save(assets/'05.png');encode_still(assets/'05.png',16,assets/'05.mp4');segments.append(assets/'05.mp4')
    evidence=base('What the evidence proves','Inspect raw model behavior separately from composited preservation.')
    d=ImageDraw.Draw(evidence);text(d,(65,232),'• Frozen cases and explicit acceptance criteria\n• Exact graphs, inputs, masks, conditioning and model revisions\n• All frames, failed runs, logs and resource measurements\n• Blinded review packet and executable analysis commands\n• Independent professional scoring is still pending',29,width=78,spacing=17)
    evidence.save(assets/'06.png');encode_still(assets/'06.png',14,assets/'06.mp4');segments.append(assets/'06.mp4')
    end=base('Run it and inspect the evidence')
    d=ImageDraw.Draw(end);text(d,(65,227),'github.com/bobfromarcher/montfortmini',39,width=53,fill=ACCENT)
    text(d,(65,331),'Short 8fps clips. Manual edit regions.\nRealistic motion, identity and lighting remain inconsistent.\nMIT application code; upstream licenses retained.',30,width=77)
    text(d,(65,535),'A transparent experimental entry, with limits shown.',27,width=75)
    end.save(assets/'07.png');encode_still(assets/'07.png',10,assets/'07.mp4');segments.append(assets/'07.mp4')
    listing=assets/'concat.txt';listing.write_text(''.join("file '"+p.name+"'\n" for p in segments), encoding='utf-8')
    final=output/'montfortmini-demo.mp4';subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(listing),'-c','copy','-movflags','+faststart',str(final)],check=True,timeout=120)
    meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(final)]))
    if float(meta['format']['duration'])>120:raise ValueError('Demo exceeds competition length')
    (output/'demo-provenance.json').write_text(json.dumps({'duration_seconds':float(meta['format']['duration']),'sha256':hashlib.sha256(final.read_bytes()).hexdigest(),'assets':provenance,'audio':'none; captioned','processing':'Layout, contain resizing, repeated playback and H264 encoding only. Actual model clips remain 8fps.'},indent=2), encoding='utf-8')
    print(final,meta['format']['duration'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--samples',required=True);p.add_argument('--ui');p.add_argument('--output',required=True);a=p.parse_args();main(a.samples,a.ui,a.output)
