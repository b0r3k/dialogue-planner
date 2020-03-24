from dialmonkey.component import Component 
from dialmonkey.da import DAI,DA
from itertools import chain
import re

class NotMatched:
    def __init__(self):
        pass

def create_intent_formatter(intent, **default_slots):
    def formatter(**x):
        args = [f'{k}={v}' if v != '' else f'{k}' for k,v in chain(default_slots.items(), x.items())]
        return f"{intent}({','.join(args)})"
    return formatter

def regex_parser(reg, formatter, required=False, **parsers):
    expr = re.compile(reg)
    def call(x):
        match = expr.match(x)
        if match:
            values = dict() 
            for key, value in match.groupdict().items():
                if key in parsers:
                    value = parsers[key](value)
                if isinstance(value, NotMatched):
                    return value
                if value is not None:
                    values[key] = value
            return formatter(**values)
        elif required:
            return NotMatched()
        else:
            return None
    return call

def dict_parser(required = False, **kwargs):
    def call(x):
        if x not in kwargs:
            if required:
                return NotMatched()
            else:
                return None
        return kwargs.get(x)
    return call

def serial_parser(*parsers):
    def call(x):
        for f in parsers:
            result = f(x)
            if result is not None and not isinstance(result, NotMatched):
                return result
        return None
    return call

planets = ['mercury','venus','earth','mars','jupiter','saturn','uranus','neptune']
r_our_planet = 'our planet|us|earth|the planet earth'.split('|')
r_start = r'^(?:thanks\,\s+|thanks\s+|ok\,\s+|ok\s+|can i ask you,\s+|can i ask you\s+|)'
def single_solar_object_parser(obj, obj_kwargs = None):
    if obj_kwargs is None:
        obj_kwargs = dict(object=obj.replace(' ','_'))
    furthest_regex = "|".join(["furthest from " + x for x in r_our_planet])
    closest_regex = "|".join(["closest to " + x for x in r_our_planet]) + '|' + "|".join(["nearest to " + x for x in r_our_planet])
    return serial_parser(
        regex_parser(r_start + fr'(?:what|which) is the (?P<property>\w+) {obj}(?: in this solar system| in the solar system| in our solar system| in our sky| in the sun solar system|)\?$', create_intent_formatter('request_single', **obj_kwargs),
            property=dict_parser(True, largest='largest', biggest='largest', smallest='smallest', furthest='furthest', nearest='closest', closest='closest', brightest='brightest')),
        regex_parser(r_start + fr'(?:what|which) {obj} is the (?P<property>\w+)(?: in this solar system| in the solar system| in our sky| in the sun solar system| to us| to earth| to our planet|)\?$', create_intent_formatter('request_single', **obj_kwargs),
            property=dict_parser(True, largest='largest', biggest='largest', smallest='smallest', furthest='furthest', nearest='closest', closest='closest', brightest='brightest')),
        regex_parser(r_start + fr'(?:what|which) is the {obj} (?:{closest_regex})(?: in this solar system| in the solar system| in our sky| in the sun solar system|)\?$', 
            create_intent_formatter('request_single', property='closest',**obj_kwargs)),
        regex_parser(r_start + fr'(?:what|which) is the {obj} (?:{furthest_regex})(?: in this solar system| in the solar system| in our sky| in the sun solar system|)\?$', 
            create_intent_formatter('request_single', property='furthest',**obj_kwargs))
    )
    


formatter = serial_parser(
    regex_parser(r'^(?:^hello|hi|ciao|hey)(?:,|) can i ask you something\?$', create_intent_formatter('greet', question = '')),
    regex_parser(r'^(?:^hello|hi|ciao|hey).*$', create_intent_formatter('greet')),
    single_solar_object_parser('planet'),
    single_solar_object_parser('dwarf planet'),
    single_solar_object_parser('comet'),
    single_solar_object_parser('asteroid'),
    single_solar_object_parser('moon'),
    single_solar_object_parser('solar body'),
    single_solar_object_parser('gas giant', dict(object='planet', type='gas_giant')),
    regex_parser(r_start + fr'which planets are (?P<property>bigger|smaller) than (?:us|Earth|planet Earth|the planet Earth)\?$', create_intent_formatter('request_filter_compare', compared_to='earth',object='planet')),
    regex_parser(r_start + fr'which planets are (?P<property>bigger|smaller) than (?:the planet |planet |)(?P<compared_to>{"|".join(planets)})\?$', create_intent_formatter('request_filter_compare', object='planet')),
    regex_parser(r_start + fr'how many planets are (?P<property>bigger|smaller) than (?:the planet |planet |)(?P<compared_to>{"|".join(planets)})\?$', create_intent_formatter('request_filter_compare', count='', object='planet')),
    regex_parser(r_start + fr'how many planets (?:there |)are (?:in the solar system|in our solar system)\?$', create_intent_formatter('request_filter_compare', count='', object='planet')),
    regex_parser(r_start + fr'what are the moons of (?:the planet |planet |)(?P<parent>{"|".join(planets)})\?$', create_intent_formatter('request_child_objects', object='moon', parent_object='planet')),
    regex_parser(r_start + fr'what moons does (?:the planet |planet |)(?P<parent>{"|".join(planets)}) have\?$', create_intent_formatter('request_child_objects', object='moon', parent_object='planet')),
    regex_parser(r_start + fr'how many moons does (?:the planet |planet |)(?P<parent>{"|".join(planets)}) have\?$', create_intent_formatter('request_child_objects', object='moon', count='', parent_object='planet')),
    regex_parser(r_start + fr'how long (?:will|would|does) it take (?:us |a rocket |a starship |)to get to (?:the planet |planet |the |)(?P<object>\w+)\?$', create_intent_formatter('request_travel_time', )),
    regex_parser(r_start + fr'how (?P<property>big|small) is (?:the planet | the|)(?P<object>\w+)\?$', create_intent_formatter('request_property')),
    regex_parser(r_start + fr'did (?:not |)(?:we|humans) (?:ever |)(?:land|landed) on (?:the |the planet |)(?P<object>\w+)(?: already|)\?$',
        create_intent_formatter('request_humans_landed')),
    regex_parser(r_start + fr'what is (?P<object>\w+)\?$', create_intent_formatter('request')),
    regex_parser(r'^(?:^bye|thanks|goodbye).*$', create_intent_formatter('goodbye')),
)

def simplify(x):
    x = x.lower()
    x = x.replace('n\'t', ' not').replace('\'m', ' am')
    return x

def evaluate(x):
    x = simplify(x)
    result = formatter(x)
    if isinstance(result, NotMatched):
        return None
    return result


class SolarSystemNLU(Component):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def __call__(self, dial, logger):
        result = evaluate(dial['user'])
        if result is not None:
            dial['nlu'].append(DA.parse_cambridge_da(result))

        logger.info('NLU: %s', str(dial['nlu']))
        return dial
