import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

SCRIPT=Path(__file__).resolve().parents[1]/'extract_checked_panels.py'
spec=importlib.util.spec_from_file_location('extractor', SCRIPT)
extractor=importlib.util.module_from_spec(spec)
spec.loader.exec_module(extractor)

class ExtractorTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.clean=Image.new('RGB',(360,240),(20,45,160))
        pen=ImageDraw.Draw(self.clean)
        pen.rectangle((120,0,239,119),fill=(230,140,40))
        pen.rectangle((0,0,119,6),fill='white') # intentional artwork border
        self.clean.save(self.root/'clean.png')
        marked=self.clean.copy()
        ImageDraw.Draw(marked).line([(20,60),(40,85),(80,30)],fill=(0,200,255),width=10)
        marked.save(self.root/'marked.png')

    def run_cli(self, *args):
        return subprocess.run([sys.executable,str(SCRIPT),'--clean',str(self.root/'clean.png'),
            '--rows','2','--cols','3','--out',str(self.root/'out'),*args],
            capture_output=True,text=True)

    def test_cyan_check_not_existing_blue_and_clean_pixels(self):
        result=self.run_cli('--marked',str(self.root/'marked.png'),'--expected','1','--square-mode','keep')
        self.assertEqual(result.returncode,0,result.stderr)
        with Image.open(self.root/'out/sheet01_01_r1_c1.png') as output:
            np.testing.assert_array_equal(np.array(output), np.array(self.clean.crop((0,0,120,120))))
        report=json.loads((self.root/'out/selection_report.json').read_text())
        self.assertEqual(report['count'],1)
        self.assertEqual(report['sheets'][0]['panels'][0]['box'],[0,0,120,120])

    def test_expected_mismatch_writes_nothing(self):
        result=self.run_cli('--marked',str(self.root/'marked.png'),'--expected','2','--zip')
        self.assertEqual(result.returncode,3)
        self.assertFalse((self.root/'out').exists())

    def test_duplicate_and_out_of_bounds_and_invalid_grid(self):
        for args in [('1,1;1,1',),('0,1',),('3,1',)]:
            result=self.run_cli('--manual',args[0])
            self.assertEqual(result.returncode,2,result.stdout)
            self.assertFalse((self.root/'out').exists())
        result=self.run_cli('--manual','1,1','--rows','0')
        self.assertEqual(result.returncode,2)

    def test_non_square_padding_keeps_all_pixels(self):
        image=Image.new('RGB',(130,80),'red')
        padded=extractor.make_square(image)
        self.assertEqual(padded.size,(130,130))
        np.testing.assert_array_equal(np.array(padded.crop((0,25,130,105))),np.array(image))
        self.assertEqual(extractor.make_square(image,'keep').size,(130,80))

    def test_zip_has_only_current_panels_and_report(self):
        result=self.run_cli('--manual','1,1;2,3','--expected','2','--zip')
        self.assertEqual(result.returncode,0,result.stderr)
        with zipfile.ZipFile(self.root/'out/selected_panels.zip') as archive:
            self.assertEqual(set(archive.namelist()),{
                'sheet01_01_r1_c1.png','sheet01_02_r2_c3.png','selection_report.json'})

    def test_overwrite_rejected(self):
        self.assertEqual(self.run_cli('--manual','1,1').returncode,0)
        target=self.root/'out/sheet01_01_r1_c1.png'
        before=target.read_bytes()
        result=self.run_cli('--manual','1,1')
        self.assertEqual(result.returncode,2)
        self.assertEqual(target.read_bytes(),before)

    def test_aspect_mismatch_rejected(self):
        Image.new('RGB',(200,200),'cyan').save(self.root/'marked.png')
        result=self.run_cli('--marked',str(self.root/'marked.png'))
        self.assertEqual(result.returncode,2)
        self.assertFalse((self.root/'out').exists())

    def test_manifest_collision_rejected_before_export(self):
        jobs=[dict(clean='clean.png',manual='1,1',prefix='same',rows=2,cols=3)]*2
        (self.root/'batch.json').write_text(json.dumps(jobs))
        result=subprocess.run([sys.executable,str(SCRIPT),'--manifest',str(self.root/'batch.json'),
          '--out',str(self.root/'out')],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertFalse((self.root/'out').exists())

    def test_gutter_and_upscale(self):
        result=self.run_cli('--manual','1,1','--gutter','7','--square-mode','keep','--upscale','2')
        self.assertEqual(result.returncode,0,result.stderr)
        with Image.open(self.root/'out/sheet01_01_r1_c1.png') as image:
            self.assertEqual(image.size,(212,212))
        report=json.loads((self.root/'out/selection_report.json').read_text())
        self.assertEqual(report['sheets'][0]['panels'][0]['box'],[7,7,113,113])

if __name__=='__main__':
    unittest.main()
