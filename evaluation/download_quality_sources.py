"""Download hash-pinned original quality-test recordings; no inference."""
import argparse,hashlib,json,urllib.request
from pathlib import Path


def main(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    records=json.loads(Path(__file__).with_name('quality_sources.json').read_text(encoding='utf-8'))
    for record in records:
        name=record['name']
        if name not in ('bee','pushup'):raise ValueError('Unexpected source name')
        path=output/(name+'.webm')
        if not path.exists():
            request=urllib.request.Request(record['imageinfo']['url'],headers={'User-Agent':'montfortmini-quality-reproduction/1.0'})
            with urllib.request.urlopen(request,timeout=90) as response:path.write_bytes(response.read())
        if hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:raise ValueError('Original recording differs from frozen bytes: '+name)
        (output/(name+'.json')).write_text(json.dumps(record,indent=2), encoding='utf-8');print('Verified',name,record['bytes'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();main(a.output)
