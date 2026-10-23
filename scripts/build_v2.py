"""Build version two without changing the version-one output or its source data."""
from pathlib import Path
import copy, hashlib, json, math, shutil
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from build import Builder, read, ROOT

SHARED = ('projects', 'papers', 'patents', 'books', 'awards')
PRIVATE = ('news', 'members', 'resources')

def load_records(folder):
    values = []
    for path in sorted(folder.glob('*.json')):
        value = read(path)
        if not isinstance(value, dict):
            raise ValueError(f'{path}: record must be an object')
        if value.get('published') is not True:
            continue
        value = copy.deepcopy(value)
        value['id'] = path.stem
        order = value.get('order') if value.get('order') is not None else 9999
        if isinstance(order, bool) or not isinstance(order, (int, float)) or not math.isfinite(order):
            raise ValueError(f'{path}: order must be a finite number')
        if not str(value.get('title', value.get('name', ''))).strip():
            raise ValueError(f'{path}: missing title/name')
        value['order'] = order
        values.append(value)
    return values

def build_v2(root=ROOT, dest=None):
    root = Path(root).resolve()
    source = root / 'versions/v2'
    dest = Path(dest or root / '_site/v2').resolve()
    if not dest.is_relative_to(root) or dest in (root, source) or source.is_relative_to(dest):
        raise ValueError('Unsafe version-two output directory')
    if dest.exists():
        shutil.rmtree(dest)
    (dest / 'assets').mkdir(parents=True)
    for name in ('site.css', 'site.js', 'school-logo.png', 'avatar-default.png'):
        shutil.copy2(source / 'assets' / name, dest / 'assets' / name)
    shutil.copy2(source / 'index.html', dest / 'index.html')
    data = {'profile': read(root / 'data/profile.json'),
            'settings': read(source / 'data/settings.json'), 'collections': {}}
    settings = data['settings']
    try:
        page_size = int(settings.get('pageSize', 10))
    except (ValueError, TypeError):
        raise ValueError('Version-two pageSize must be 10, 20 or 50')
    if page_size not in (10, 20, 50):
        raise ValueError('Version-two pageSize must be 10, 20 or 50')
    settings['pageSize'] = page_size
    overrides = {}
    for path in sorted((source / 'content/overrides').glob('*.json')):
        value = read(path)
        if value.get('published') is not True:
            continue
        key = (value.get('collection'), value.get('recordId'))
        if key in overrides:
            raise ValueError(f'Duplicate version-two override: {key}')
        if key[0] not in SHARED:
            raise ValueError('Overrides may only target shared academic records')
        overrides[key] = value
    used = set()
    allowed = ('body', 'summary', 'images', 'cover', 'video', 'videoUrl', 'poster',
               'attachment', 'showOnHome', 'order')
    for kind in SHARED + PRIVATE:
        folder = root / 'content' / kind if kind in SHARED else source / 'content' / kind
        records = load_records(folder)
        result = []
        for value in records:
            key = (kind, value['id'])
            override = overrides.get(key)
            if override:
                used.add(key)
                if override.get('hidden') is True:
                    continue
                for field in allowed:
                    if field in override and override[field] is not None:
                        value[field] = override[field]
            if kind == 'resources' and value.get('target') not in (None, '', 'resources', 'home', 'lab', 'news', 'team', 'research', 'admissions'):
                raise ValueError('Invalid version-two resource target')
            result.append(value)
        for value in result:
            order = value.get('order') if value.get('order') is not None else 9999
            if isinstance(order, bool) or not isinstance(order, (int, float)) or not math.isfinite(order):
                raise ValueError('Override order must be a finite number')
        result.sort(key=lambda v: str(v.get('date', '')), reverse=True)
        result.sort(key=lambda v: (not bool(v.get('pinned')) if kind == 'news' else False,
                                   v.get('order', 9999), v['id'] if not v.get('date') else ''))
        data['collections'][kind] = result
    if set(overrides) - used:
        raise ValueError('Override points to a missing or unpublished shared record: ' + str(set(overrides) - used))
    settings.pop('recordOverrides', None)
    assets = Builder(root, dest)
    def asset(value, image=False):
        if not value:
            return ''
        if not isinstance(value, str):
            raise ValueError('Asset/link must be a string')
        value = assets.source(value)
        if image:
            markup = assets.image(value)
            return BeautifulSoup(markup, 'html.parser').img['src']
        if value and not urlsplit(value).scheme:
            target = dest / value
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / value, target)
        return value
    def media(record):
        images = record.get('images', []) or []
        if not isinstance(images, list):
            raise ValueError('images must be a list')
        record['images'] = [asset(i, True) if isinstance(i, str) else
                            {'url': asset(i.get('url'), True), 'caption': str(i.get('caption', ''))}
                            for i in images]
        for key in ('photo', 'portrait', 'poster', 'cover'):
            if record.get(key):
                if key == 'cover' and isinstance(record[key], dict):
                    record[key] = {'url': asset(record[key].get('url'), True),
                                   'caption': str(record[key].get('caption', ''))}
                else:
                    record[key] = asset(record[key], True)
        for key in ('video', 'videoUrl', 'attachment', 'link', 'source', 'homepage'):
            if record.get(key):
                record[key] = asset(record[key])
    media(data['profile'])
    for admission in data['profile'].get('admissions', []):
        admission['url'] = asset(admission.get('url'))
    if settings.get('teacherHomepage'):
        settings['teacherHomepage'] = asset(settings['teacherHomepage'])
    slides = []
    for slide in settings.get('slides', []):
        if slide.get('published') is True and slide.get('image'):
            slide = copy.deepcopy(slide)
            slide['image'] = asset(slide['image'], True)
            slides.append(slide)
    settings['slides'] = slides
    for records in data['collections'].values():
        for record in records:
            media(record)
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    (dest / 'assets/data.js').write_text('window.SITE_DATA = ' + payload + ';\n', encoding='utf-8')
    # A newly published HTML page must not reuse a previous release's cached data/runtime.
    document = BeautifulSoup((dest / 'index.html').read_text(encoding='utf-8'), 'html.parser')
    for node in document.select('script[src], link[rel=stylesheet][href]'):
        attr = 'src' if node.name == 'script' else 'href'
        name = node[attr]
        if name in ('assets/data.js', 'assets/site.js', 'assets/site.css'):
            digest = hashlib.sha256((dest / name).read_bytes()).hexdigest()[:16]
            node[attr] = name + '?v=' + digest
    (dest / 'index.html').write_text(str(document), encoding='utf-8')
    return {'published': {k: len(v) for k, v in data['collections'].items()},
            'dataBytes': len(payload.encode('utf-8')), 'path': 'v2/'}

if __name__ == '__main__':
    print(json.dumps(build_v2(), ensure_ascii=False))
