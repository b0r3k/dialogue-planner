from ..component import Component
from ..da import DAI
import cloudpickle
import numpy as np
import os


class KulhanekNLU(Component):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(os.path.join(os.path.dirname(__file__), 'kulhanek-model.pkl'), 'rb') as f:
            self._classify_text_full = cloudpickle.load(f)

    def _classify_text(self, text, proba_treshold = 0.5, nalternative  = None):
        result = [(x, p) for x,p in self._classify_text_full(text) if p >= proba_treshold]
        if nalternative is not None:
            altlist = [(x,p) for x,p in self._classify_text_full(text) if p < proba_treshold]
            altlist.sort(key=lambda x: -x[1])
            result.extend(altlist[:nalternative])
        return result

    def __call__(self, dial, logger): 
        all_hypothesis = self._classify_text(dial['user'], self.cfg.get('probability_treshold', 0.5), self.cfg.get('nalternatives', None))
        for dia, p in all_hypothesis:
            dial['nlu'].append(DAI(*dia, confidence=p)) 

        logger.info('NLU: %s', str(dial['nlu']))
        return dial
