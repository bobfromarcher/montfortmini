"""Download only the four hash-pinned, openly licensed evaluation recordings."""
import argparse,hashlib,json,urllib.request
from pathlib import Path

def main(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    for record in json.loads(Path(__file__).with_name('sources.json').read_text(encoding='utf-8-sig')):
        target=output/(record['name']+'.webm')
        if not target.exists():
            request=urllib.request.Request(record['download_url'],headers={'User-Agent':'montfortmini-validation/1.0'})
            with urllib.request.urlopen(request,timeout=90) as response:target.write_bytes(response.read())
        if hashlib.sha256(target.read_bytes()).hexdigest()!=record['sha256']:raise ValueError('Source hash mismatch: '+record['name'])
        # Build the metadata shape expected by build_dataset, retaining attribution.
        (output/(record['name']+'.json')).write_text(json.dumps({**record,'imageinfo':{'url':record['download_url'],
            'extmetadata':{'LicenseShortName':{'value':record['license']},'LicenseUrl':{'value':record['license_url']},'Artist':{'value':record['author_html']}}}},indent=2))
        print(record['name'],record['license'],flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();main(args.output)
