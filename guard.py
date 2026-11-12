#!/usr/bin/env python3
"""Validate storage identity before starting a writer; never mount or format."""
import argparse,json,os,shutil,subprocess
from pathlib import Path

def validate(c):
    p=Path(c['mountpoint'])
    if not p.is_absolute() or p.is_symlink() or not os.path.ismount(p):raise ValueError('Expected a mounted absolute path')
    result=subprocess.check_output(['findmnt','--json','-M',str(p),'-o','TARGET,UUID,FSTYPE,OPTIONS'],text=True,timeout=5)
    rows=json.loads(result)['filesystems']
    if len(rows)!=1 or rows[0]['target']!=str(p):raise ValueError('Ambiguous mount')
    fs=rows[0]
    if not c.get('uuid') or fs.get('uuid')!=c['uuid']:raise ValueError('Wrong disk UUID')
    if c.get('fstype') and fs.get('fstype')!=c['fstype']:raise ValueError('Wrong filesystem')
    if 'ro' in fs.get('options','').split(','):raise ValueError('Read-only filesystem')
    if shutil.disk_usage(p).free<c.get('minimum_free_bytes',0):raise ValueError('Insufficient free space')
    for name in c.get('directories',[]):
        q=p/name
        if Path(name).is_absolute() or '..' in Path(name).parts or q.is_symlink() or not q.is_dir() or q.stat().st_dev!=p.stat().st_dev:raise ValueError('Invalid required directory')
    return {'ok':True,'mountpoint':str(p)}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('config');a=ap.parse_args()
    try:print(json.dumps(validate(json.loads(Path(a.config).read_text()))));return 0
    except Exception as e:print(json.dumps({'ok':False,'error':str(e)}));return 1
if __name__=='__main__':raise SystemExit(main())
