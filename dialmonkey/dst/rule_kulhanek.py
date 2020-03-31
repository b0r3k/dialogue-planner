from ..component import Component 
from ..da import DAI, DA
from itertools import groupby
from collections import defaultdict

class KulhanekDST(Component): 
    def __call__(self, dial, logger):
        if dial['state'] is None: dial['state'] = dict()
        nlu: DA = dial['nlu']
        slot_value_p = [(x.slot, x.value, x.confidence) for x in nlu.dais]
        slot_value_p.sort()
        slot_value_p = [(slot, value, sum(map(lambda x: x[-1], x))) for (slot,value), x in groupby(slot_value_p, key=lambda x:x[:-1])]
        for slot, values in groupby(slot_value_p, key=lambda x: x[0]):
            if not slot in dial['state']: dial['state'][slot] = { None: 1.0 }
            conf = dial['state'][slot]
            value_conf = { k: v for _, k, v in values }
            value_conf[None] = 1.0 - sum(value_conf.values()) 
            for key in set(value_conf.keys()).union(set(conf.keys())):
                conf[key] = conf.get(key, 0.0) * value_conf[None] + value_conf.get(key, 0.0) 
            conf[None] = 0.0
            conf[None] = 1.0 - sum(conf.values())

        logger.info('State: %s', str(dial['state']))
        return dial
