"""Build checks use an isolated copy; synthetic records are never published."""
import unittest,tempfile,shutil,json,sys
from pathlib import Path
from bs4 import BeautifulSoup
sys.path.insert(0,str(Path(__file__).parent));from build import build,ROOT
class BuildTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix="qa-",dir=ROOT);self.root=Path(self.temp.name)/'repo';self.root.mkdir()
  for name in ['assets','media','templates','data','content']:shutil.copytree(ROOT/name,self.root/name)
  # Tests must not depend on the number of records maintained by real editors.
  for folder in (self.root/'content').iterdir():
   for record in folder.glob('*.json'):
    assert record.resolve().is_relative_to(self.root.resolve())
    record.unlink()
  for i in range(12):self.put('papers',f'baseline-{i:02}',dict(title=f'Test paper {i}',citation=f'Test citation {i}',doi='',link='',published=True,order=i))
 def tearDown(self):
  assert Path(self.temp.name).resolve().is_relative_to(ROOT.resolve())
  self.temp.cleanup()
 def put(self,key,name,record):
  (self.root/'content'/key/(name+'.json')).write_text(json.dumps(record,ensure_ascii=False),encoding='utf-8')
 def page(self):
  build(self.root);return BeautifulSoup((self.root/'_site/index.html').read_text(encoding='utf-8'),'html.parser')
 def test_original_data_and_small_initial_page(self):
  doc=self.page();data=json.loads(doc.select_one('#cms-page-data').string)
  self.assertEqual(len(data['groups']['papers']),12);self.assertEqual(len(doc.select('.publications > li')),10)
  self.assertFalse((self.root/'_site/content').exists());self.assertFalse((self.root/'_site/.pages.yml').exists())
  self.assertLess((self.root/'_site/index.html').stat().st_size,60000)
  self.assertTrue(doc.select_one('#tab-news'));self.assertTrue(doc.select_one('#tab-resources'))
 def test_many_records_order_and_unpublished_exclusion(self):
  for i in range(1000):self.put('news',f'n{i:04}',dict(title=f'QA-{i}',body='layout only',date='2026-10-21',published=True,order=i,images=[]))
  self.put('news','draft',dict(title='PRIVATE-DRAFT-MARKER',body='not public',published=False,order=0))
  self.put('news','pinned',dict(title='PINNED',published=True,pinned=True,order=99999))
  doc=self.page();data=json.loads(doc.select_one('#cms-page-data').string)
  self.assertEqual(len(data['groups']['news']),1001);self.assertEqual(len(doc.select('#news .cms-record')),10)
  self.assertEqual(doc.select_one('#news h3').text,'PINNED');self.assertNotIn('PRIVATE-DRAFT-MARKER',str(doc))
 def test_safe_text_attachment_and_missing_file(self):
  self.put('news','text',dict(title='<img src=x onerror=alert(1)>',body='<script>BAD()</script>',published=True,order=1))
  doc=self.page();self.assertFalse(doc.select('#news script'));self.assertIn('<script>BAD()</script>',doc.select_one('#news').text)
  self.put('resources','bad',dict(title='bad',published=True,attachment='../../outside.pdf'))
  with self.assertRaises(ValueError):self.page()
 def test_dangerous_url_rejected(self):
  self.put('members','bad',dict(name='bad',published=True,link='javascript:alert(1)'))
  with self.assertRaises(ValueError):self.page()
 def test_resource_position_and_media(self):
  (self.root/'media/files/test.pdf').write_bytes(b'%PDF-1.4\n%QA only')
  self.put('resources','r',dict(title='POSITION-MARKER',published=True,target='research',position='before',attachment='media/files/test.pdf'))
  doc=self.page();self.assertEqual(doc.select_one('#research > section h3').text,'POSITION-MARKER');self.assertTrue(doc.select_one('#research a[href="media/files/test.pdf"]'))
if __name__=='__main__':unittest.main()
