import copy, hashlib, json, shutil, tempfile, unittest
from pathlib import Path
from build import ROOT, build
from build_v2 import build_v2

class VersionTwoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='hao-v2-test-', dir=ROOT.parent)
        self.root = Path(self.temp.name) / 'project'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('_site', '__pycache__'))
        self.v2 = self.root / 'versions/v2'
    def tearDown(self):
        self.temp.cleanup()
    def write(self, path, obj):
        path = self.root / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj, ensure_ascii=False), encoding='utf-8')
    def data(self):
        build_v2(self.root)
        text = (self.root / '_site/v2/assets/data.js').read_text(encoding='utf-8')
        return json.loads(text.removeprefix('window.SITE_DATA = ').rstrip(';\n'))
    def test_first_version_output_is_unchanged(self):
        build(self.root)
        before = {str(p.relative_to(self.root / '_site')): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in (self.root / '_site').rglob('*') if p.is_file()}
        build_v2(self.root)
        for name, digest in before.items():
            self.assertEqual(hashlib.sha256((self.root / '_site' / name).read_bytes()).hexdigest(), digest)
    def test_version_specific_isolation_and_hidden_drafts(self):
        self.write('content/news/only-v1.json', {'title':'V1 ONLY', 'published':True})
        self.write('versions/v2/content/news/only-v2.json', {'title':'V2 ONLY', 'published':True})
        self.write('versions/v2/content/news/draft.json', {'title':'SECRET DRAFT', 'published':False})
        data = self.data()
        self.assertEqual([x['title'] for x in data['collections']['news']], ['V2 ONLY'])
    def test_shared_profile_is_live_not_a_frozen_copy(self):
        path = self.root / 'data/profile.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        data['directions'] = ['Changed shared direction']
        self.write('data/profile.json', data)
        self.assertEqual(self.data()['profile']['directions'], ['Changed shared direction'])
    def test_override_does_not_change_shared_record(self):
        original = (self.root / 'content/projects/projects-001.json').read_bytes()
        self.write('versions/v2/content/overrides/test.json', {'title':'override','collection':'projects',
                   'recordId':'projects-001','body':'V2 extra','order':0,'published':True})
        self.assertEqual(self.data()['collections']['projects'][0]['body'], 'V2 extra')
        self.assertEqual((self.root / 'content/projects/projects-001.json').read_bytes(), original)
    def test_duplicate_or_missing_override_fails(self):
        self.write('versions/v2/content/overrides/test.json', {'title':'override','collection':'projects',
                   'recordId':'missing','published':True})
        with self.assertRaises(ValueError): self.data()
    def test_media_optimized_and_missing_media_rejected(self):
        from PIL import Image
        path = self.root / 'media/images/v2-test.png'
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new('RGB',(2400,1600),'navy').save(path)
        record = {'title':'media','published':True,'images':['media/images/v2-test.png']}
        self.write('versions/v2/content/news/media.json', record)
        image = self.data()['collections']['news'][0]['images'][0]
        with Image.open(self.root / '_site/v2' / image) as im: self.assertLessEqual(im.width, 1600)
        record['images'] = ['media/images/missing.png']
        self.write('versions/v2/content/news/media.json', record)
        with self.assertRaises(ValueError): self.data()
    def test_dangerous_url_and_oversize_rejected(self):
        record = {'title':'bad link','published':True,'link':'javascript:alert(1)'}
        self.write('versions/v2/content/resources/bad.json', record)
        with self.assertRaises(ValueError): self.data()
        record.pop('link'); record['video']='media/videos/large.webm'
        path=self.root/record['video'];path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('wb') as f: f.truncate(20*1024*1024+1)
        self.write('versions/v2/content/resources/bad.json', record)
        with self.assertRaises(ValueError): self.data()
    def test_large_records_order_and_no_draft_leak(self):
        for i in range(1001):
            self.write(f'versions/v2/content/news/news-{i:04}.json',
                       {'title':f'News {i}', 'order':i,'published':True,'pinned':i==1000})
        records = self.data()['collections']['news']
        self.assertEqual(len(records), 1001)
        self.assertEqual(records[0]['title'], 'News 1000')
        self.assertEqual(records[1]['title'], 'News 0')
    def test_invalid_page_size_rejected(self):
        path=self.v2/'data/settings.json';data=json.loads(path.read_text(encoding='utf-8'))
        data['pageSize']=0;self.write('versions/v2/data/settings.json',data)
        with self.assertRaises(ValueError): self.data()

if __name__ == '__main__': unittest.main()
