"""Staged, one-attempt replay of the current native backend; no deployment.

Requires a fresh frozen packet. Prepare controls, review them, then render once.
Uses native_motion_backend.prepare/render unchanged; not an HTTP/browser test.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import zipfile

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['controls', 'render'])
    parser.add_argument('directory', type=Path)
    parser.add_argument('--confirm-credits-only', action='store_true')
    args = parser.parse_args()
    root = args.directory.resolve()
    frozen = read(root/'freeze.json')
    if not args.confirm_credits_only or frozen['budget']['cash_cap'] != 0 or frozen['budget']['included_cap'] != 1:
        raise ValueError('Frozen $1 included-credit cap and live zero-cash check required')
    for name, sha in frozen['source_sha256'].items():
        if digest(HERE/name) != sha:
            raise ValueError('Source changed: '+name)
    for name, sha in frozen['artifact_sha256'].items():
        if digest(root/name) != sha:
            raise ValueError('Frozen input changed: '+name)
    import native_motion_backend as backend
    from native_recipe_fixture import validate_fixture
    stage = args.stage
    ledger = root/(stage+'-ledger.json')
    if ledger.exists():
        raise ValueError('Attempt already reserved; no retry')
    if stage == 'render':
        review = read(root/'controls-review.json')
        if not review.get('gate_pass') or review['inputs_sha256'] != digest(root/'inputs.zip'):
            raise ValueError('Prepared controls must be reviewed before GPU dispatch')
        graph = read(root/'workflow-api.json')
        if graph != frozen['expected_graph']:
            raise ValueError('Graph changed')
        shape = graph['7']['inputs']
        validate_fixture((root/'inputs.zip').read_bytes(), frames=shape['length'], width=shape['width'], height=shape['height'])
    row = {'stage':stage, 'status':'reserved', 'max_calls':1, 'max_worker_seconds':900}
    ledger.write_text(json.dumps(row, indent=2), encoding='utf-8')
    started = time.monotonic()
    try:
        with backend.app.run():
            if stage == 'controls':
                call = backend.prepare.spawn(read(root/'request.json'))
            else:
                call = backend.render.spawn((root/'inputs.zip').read_bytes(), graph)
            row.update(status='dispatched', call_id=call.object_id)
            ledger.write_text(json.dumps(row, indent=2), encoding='utf-8')
            print(stage+' receipt: '+call.object_id, flush=True)
            result = call.get()
            if stage == 'controls':
                (root/'inputs.zip').write_bytes(result['inputs'])
                (root/'workflow-api.json').write_text(json.dumps(result['graph'], indent=2), encoding='utf-8')
                if result['graph'] != frozen['expected_graph']:
                    raise ValueError('Actual preparation graph differs from freeze')
            else:
                dest = root/'result'
                dest.mkdir(exist_ok=False)
                (dest/'evidence.zip').write_bytes(result)
                with zipfile.ZipFile(io.BytesIO(result)) as archive:
                    if any(not (dest/i.filename).resolve().is_relative_to(dest) for i in archive.infolist()):
                        raise ValueError('Unsafe evidence archive')
                    archive.extractall(dest)
                if read(dest/'candidate.json')['status'] != 'succeeded':
                    raise RuntimeError('Technical failure retained; stop')
            row['status'] = 'succeeded'
    except Exception as exc:
        row.update(status='failed', exception_type=type(exc).__name__)
        raise
    finally:
        row['client_elapsed_seconds'] = time.monotonic()-started
        ledger.write_text(json.dumps(row, indent=2), encoding='utf-8')
    print(stage+' completed; no automatic next stage', flush=True)


if __name__ == '__main__':
    main()
