"""Official checkpoint/LoRA/sampler recipe at the retained diagnostic dimensions.

Not a recovered Higgsfield graph, nor a bit-exact reproduction of the full
official UI template (which uses different sizes, lengths and continuation).
"""
from explicit_motion_workflow import build_graph as prior_graph
from native_recipe_models import ASSETS


def build_graph():
    graph = prior_graph()
    graph['1']['inputs']['unet_name'] = ASSETS[0]['file'].split('/')[-1]
    graph['4']['inputs']['text'] = (
        'The person in the reference image performs the movements from the source video. '
        'Stable appearance, natural hand and body movement, fixed camera.')
    graph['15'] = {'class_type': 'LoraLoaderModelOnly', 'inputs': {
        'model': ['1', 0], 'lora_name': ASSETS[1]['file'].split('/')[-1], 'strength_model': 1.0}}
    graph['16'] = {'class_type': 'LoraLoaderModelOnly', 'inputs': {
        'model': ['15', 0], 'lora_name': ASSETS[2]['file'].split('/')[-1], 'strength_model': 1.0}}
    graph['8']['inputs'].update(model=['16', 0], shift=8.0)
    graph['9']['inputs'].update(steps=6, cfg=1.0, sampler_name='euler', scheduler='simple', seed=42)
    return graph
