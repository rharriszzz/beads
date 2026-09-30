"""Meaningful evaluator and output-preservation regressions; no GUI/server."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import auto_label_beads as auto
from label_beads import LabelStore
from PIL import Image


class AutomaticLabelTests(unittest.TestCase):
    def test_missing_mark_does_not_displace_valid_nearby_association(self):
        # Two maker marks share one nearby proposal; the other proposal is remote.
        # Forced Hungarian assignment used to steal that proposal from mark1.
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'manual.json'
            path.write_text(json.dumps(dict(revision=1,annotations=[
                dict(id='one',number=1,x=0,y=0),dict(id='two',number=2,x=5,y=0)],series=[])))
            result=dict(points=[dict(source_xy=[0,0]),dict(source_xy=[-100,0])],diameter=4,scale=np.ones(2))
            report=auto.evaluate(result,dict(edges=[]),path)
            self.assertEqual(report['matched_within_gate'],1)
            self.assertEqual(report['matches'][0]['automatic_point'],0)
            self.assertIsNone(report['matches'][1]['automatic_point'])

    def test_reviewed_and_maker_files_cannot_be_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory);target=out/'annotations.json'
            target.write_text(json.dumps(dict(automatic_proposals=True,revision=0)))
            (out/'report.json').write_text(json.dumps(dict(automatic_annotation_sha256=auto.sha(target))))
            with self.assertRaises(ValueError):auto.check_output(out)
            auto.check_output(out,True)
            target.write_text(json.dumps(dict(automatic_proposals=True,revision=1)))
            with self.assertRaises(ValueError):auto.check_output(out,True)
            target.write_text(json.dumps(dict(annotations=[])))
            with self.assertRaises(ValueError):auto.check_output(out,True)
        with self.assertRaises(ValueError):auto.check_output(auto.ROOT/'photo2/output/labeler',True)

    def test_export_opens_in_actual_labeler_and_preserves_direction(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory);image=out/'source.png';Image.new('RGB',(100,100),'white').save(image)
            result=dict(points=[dict(source_xy=[20,30]),dict(source_xy=[50,60])])
            graph=dict(edges=[dict(start=0,end=1,direction='d2')])
            original=auto.export(result,graph,image,(100,100),out)
            opened=LabelStore(image,None,out/'annotations.json').read()
            self.assertEqual(opened['annotations'],original['annotations'])
            self.assertEqual(opened['series'],original['series'])
            self.assertTrue(opened['automatic_proposals'])
            self.assertEqual(opened['series'][0]['bead_ids'],[a['id'] for a in opened['annotations']])
            store=LabelStore(image,None,out/'annotations.json')
            saved=store.save(dict(revision=0,annotations=opened['annotations'],series=opened['series']))
            self.assertTrue(saved['automatic_proposals'])
            self.assertEqual(saved['automatic_origin'],original['automatic_origin'])
            self.assertIn('confirmation is not implied',saved['annotation_kind'])


if __name__=='__main__':unittest.main()
