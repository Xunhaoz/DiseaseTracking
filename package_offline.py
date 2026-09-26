"""Create one self-contained HTML file; no upload or external resources."""
from pathlib import Path
import base64, json, mimetypes, re

project=Path(__file__).resolve().parent
dist=project/'dist'
raw=(dist/'data.js').read_text().removeprefix('window.CASE_DATA = ').strip().removesuffix(';')
data=json.loads(raw)

def inline_asset(value):
    src=dist/value
    mime=mimetypes.guess_type(src.name)[0] or 'application/octet-stream'
    return 'data:'+mime+';base64,'+base64.b64encode(src.read_bytes()).decode()

for series in data['series']:
    for image in series['images']:
        image['path']=inline_asset(image['path'])
        image['thumb']=inline_asset(image['thumb'])
for photo in data['photos']:
    photo['path']=inline_asset(photo['path'])
    photo['thumb']=inline_asset(photo['thumb'])
    photo['original']=inline_asset(photo['original'])
for doc in data['documents']: doc['path']=inline_asset(doc['path'])
html=(dist/'index.html').read_text()
for name in ['style.css','components.css']:
    html=re.sub(r'<link rel="stylesheet" href="'+re.escape(name)+r'(?:\?[^\"]*)?">',lambda _: '<style>'+(dist/name).read_text()+'</style>',html)
js='window.CASE_DATA = '+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+';'
html=re.sub(r'<script src="data.js(?:\?[^\"]*)?"></script>',lambda _: '<script>'+js+'</script>',html)
html=re.sub(r'<script src="app.js(?:\?[^\"]*)?"></script>',lambda _: '<script>'+(dist/'app.js').read_text()+'</script>',html)
out=project/'病情追蹤_離線版.html'
out.write_text(html)
assert '<script src=' not in html and '<link rel="stylesheet"' not in html
print(f'Offline HTML: {out.stat().st_size/1024/1024:.1f} MiB')
