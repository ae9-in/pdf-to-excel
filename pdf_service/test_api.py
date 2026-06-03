import requests

with open('D:/pdf to excal/TaskAllocation_TEMPLATE.pdf', 'rb') as f:
    resp = requests.post(
        'http://127.0.0.1:8000/convert',
        files={'file': ('template.pdf', f, 'application/pdf')}
    )

if resp.ok:
    d = resp.json()
    print('Tasks:', d['summary']['task_count'])
    for t in d['result']['tasks'][:15]:
        tid = t['id']
        name = t['name']
        team = t['team']
        title = t['taskTitle'][:40]
        print(f'  [{tid:2}] {name:<25} | {team:<25} | {title}')
else:
    print('Error:', resp.status_code, resp.text[:500])
