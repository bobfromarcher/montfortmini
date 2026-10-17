import base64,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import media_pipeline

class DisplayOrientation(unittest.TestCase):
    def test_display_matrix_controls_geometry_and_overrides_legacy_tag(self):
        for angle in (90,-90,270):
            with self.subTest(angle=angle):
                stream=dict(width=360,height=480,side_data_list=[{'rotation':angle}],tags={'rotate':'0'})
                self.assertEqual(media_pipeline.display_geometry(stream),(480,360))
        self.assertEqual(media_pipeline.display_geometry(dict(width=480,height=360,tags={'rotate':'180'})),(480,360))

    def test_invalid_rotation_is_not_silently_stretched(self):
        for angle in ('nan','45'):
            with self.subTest(angle=angle),self.assertRaises(ValueError):
                media_pipeline.display_geometry(dict(width=320,height=480,tags={'rotate':angle}))

    def test_real_rotated_clip_matches_canonical_pixels_and_mask(self):
        from PIL import Image,ImageDraw
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);frames=root/'frames';frames.mkdir()
            reference=Image.new('RGB',(128,192),'white');reference.save(root/'reference.png')
            for i in range(17):
                im=reference.copy();ImageDraw.Draw(im).rectangle((12+i,28,45+i,64),fill='red');im.save(frames/f'{i:04d}.png')
            def run(args):subprocess.run(args,check=True,capture_output=True,timeout=30)
            run(['ffmpeg','-y','-loglevel','error','-framerate','8','-i',str(frames/'%04d.png'),'-c:v','libx264','-pix_fmt','yuv420p',str(root/'normal.mp4')])
            run(['ffmpeg','-y','-loglevel','error','-i',str(root/'normal.mp4'),'-vf','transpose=1','-c:v','libx264',str(root/'stored.mp4')])
            run(['ffmpeg','-y','-loglevel','error','-display_rotation','90','-i',str(root/'stored.mp4'),'-c','copy',str(root/'rotated.mp4')])
            probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream_side_data=rotation','-of','json',str(root/'rotated.mp4')]))
            self.assertTrue(any(abs(s.get('rotation',0))==90 for s in probe['streams'][0].get('side_data_list',[])),"Test fixture must actually carry rotation metadata")
            payload=dict(mode='object-swap',frames=17,bbox=[.05,.1,.55,.4],end_bbox=[.05,.1,.55,.4],
                         video_b64=base64.b64encode((root/'rotated.mp4').read_bytes()).decode(),reference_b64=base64.b64encode((root/'reference.png').read_bytes()).decode())
            output=root/'prepared'
            with patch.object(media_pipeline,'Path',lambda p:output if p=='/tmp/openjutsu-fixture' else Path(p)):
                result=media_pipeline.prepare_media(payload)
            self.assertEqual((result['width'],result['height']),(320,480))
            import numpy as np
            image=np.asarray(Image.open(output/'source/0000.png').convert('RGB'))
            mask=np.asarray(Image.open(output/'masks/0000.png').convert('L'))
            red=(image[:,:,0]>150)&(image[:,:,1]<90)&(image[:,:,2]<90)
            self.assertGreater(red.sum(),1000)
            self.assertGreater(float((mask[red]>0).mean()),.98)

if __name__=='__main__':unittest.main()
