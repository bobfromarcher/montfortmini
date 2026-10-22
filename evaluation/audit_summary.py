"""Resolve the retained fixture revision and summarize measured evidence, without inference."""
import argparse,csv,json,statistics,subprocess
from pathlib import Path

def main(root):
    root=Path(root);records=[]
    for line in (root/'runs/ledger.jsonl').read_text().splitlines():
        record=json.loads(line);name=record['run'];path=root/'runs'/name
        if record.get('input_video_sha256')!=json.loads((path/'evaluation.json').read_text()).get('input_video_sha256'):
            path=root/'rejected-input-runs/dev-real-object-v1';record['analysis_status']='rejected-fixture-metadata'
        else:record['analysis_status']='included'
        record['resolved_evidence_path']=path.relative_to(root).as_posix();records.append(record)
    (root/'audited-ledger.json').write_text(json.dumps(records,indent=2))
    analysis=json.loads((root/'paired-analysis.json').read_text());metrics=json.loads((root/'metrics.json').read_text())
    resources=analysis['resources']
    with (root/'resources.csv').open('w',newline='') as f:
        fields=['run','worker_seconds','gpu_sample_count','peak_vram_MiB','mean_gpu_utilization_percent','mean_power_W']
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(resources)
    failure_file=root/'infrastructure-failures.json'
    failures=json.loads(failure_file.read_text()) if failure_file.exists() else []
    summary={'successful_generations_including_rejected_fixture':len(records),'analyzed_runs':len(metrics),
      'worker_seconds_all_successful':sum(r['worker_elapsed_seconds'] for r in records),
      'worker_seconds_analyzed':sum(r['worker_seconds'] for r in resources),
      'client_wall_seconds_all_successful':sum(r['client_wall_seconds'] for r in records),
      'startup_failures_before_sampling':len(failures),'total_attempts_including_startup_failure':len(records)+len(failures),
      'model_hash_audit_cpu_seconds':json.loads((root/'model-file-audit.json').read_text())['audit_seconds'],
      'peak_sampled_vram_MiB':max(r.get('peak_vram_MiB',0) for r in resources),
      'all_analyzed_technical_gates_pass':all(r['technical_frames_pass'] for r in metrics),
      'all_object_composite_png_outside_mask_max_255':max(r['composite_png_outside_mask']['max_255'] for r in metrics if r['mode']=='object-swap'),
      'runtime_ranges_seconds':{kind:{'min':min(r['worker_seconds'] for r in resources if kind in r['run']),
          'median':statistics.median(r['worker_seconds'] for r in resources if kind in r['run']),
          'max':max(r['worker_seconds'] for r in resources if kind in r['run'])} for kind in ('object','motion')},
      'measurement_limits':['Worker time excludes some container allocation/image startup and is not billed GPU seconds.','GPU samples are 1 Hz; transient peaks may be missed.','CPU and system RAM peak usage were not sampled; allocation was 2 CPU / 32 GiB.','Account billing is rounded/delayed, not an exact per-run cost allocation.']}
    (root/'resource-summary.json').write_text(json.dumps(summary,indent=2))
    (root/'local-environment.txt').write_text(subprocess.check_output(['ffmpeg','-version'],text=True)+ '\n'+subprocess.check_output(['ffprobe','-version'],text=True))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root');a=p.parse_args();main(a.root)
