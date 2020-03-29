from dialmonkey.nlu.solar import evaluate
import re

def assert_acts_equal(act1, act2):
    assert isinstance(act1, str)
    assert isinstance(act2, str)
    int1 = act1[:act1.index('(')]
    int2 = act1[:act2.index('(')]
    assert int1 == int2, f"different intents {act1} != {act2}"
    par1 = act1[act1.index('(') + 1:-1]
    par2 = act2[act2.index('(') + 1:-1]
    par1 = { k:v for k,v in ((x.split('=') if '=' in x else (x,'')) for x in par1.split(','))}
    par2 = { k:v for k,v in ((x.split('=') if '=' in x else (x,'')) for x in par2.split(','))}
    assert all(v == par1[k] for k,v in par2.items()) and len(par1) == len(par2), f"different acts {act1} != {act2}"

def test_greet():
    assert evaluate('Hi system!') == 'greet()'
    assert evaluate('Hello assistant') == 'greet()'
    assert evaluate('hi') == 'greet()'
    assert evaluate('hi, can I ask you something?') == 'greet(question)'

def test_goodbye():
    assert_acts_equal(evaluate('Bye'), 'goodbye()')
    assert evaluate('Thanks, that is all') == 'goodbye()'
    assert evaluate('goodbye') == 'goodbye()'

def test_what_is_the_planet():
    assert_acts_equal(evaluate('Ok, what is the largest planet?'), 'request_single(object=planet,property=largest)')
    assert_acts_equal(evaluate('What is the biggest planet?'), 'request_single(object=planet,property=largest)')
    assert_acts_equal(evaluate('What is the closest planet?'), 'request_single(object=planet,property=closest)')
    assert_acts_equal(evaluate('which planet is the closest?'), 'request_single(object=planet,property=closest)')
    assert_acts_equal(evaluate('What is the biggest asteroid in the solar system?'), 'request_single(object=asteroid,property=largest)')
    assert_acts_equal(evaluate('which is the smallest planet?'), 'request_single(object=planet,property=smallest)')
    assert_acts_equal(evaluate('What is the smallest planet in the Solar system?'), 'request_single(object=planet,property=smallest)')
    assert_acts_equal(evaluate('What is the planet closest to Earth?'), 'request_single(object=planet,property=closest)')
    assert_acts_equal(evaluate('which planet is the closest to us?'), 'request_single(object=planet,property=closest)')

def test_what_is_the_dwarf_planet():
    assert_acts_equal(evaluate('Thanks, what is the largest dwarf planet in the Sun solar system?'), 'request_single(object=dwarf_planet,property=largest)')
    assert_acts_equal(evaluate('What is the largest dwarf planet in the solar system?'), 'request_single(object=dwarf_planet,property=largest)')
    assert_acts_equal(evaluate('What is the dwarf planet furthest from us in the solar system?'), 'request_single(object=dwarf_planet,property=furthest)')

def test_which_planets_are_then_planets():
    assert_acts_equal(evaluate('Thanks, which planets are bigger than us?'), 'request_filter_compare(object=planet,property=bigger,compared_to=earth)')
    assert_acts_equal(evaluate('Thanks, which planets are bigger than the planet Mars?'), 'request_filter_compare(object=planet,property=bigger,compared_to=mars)')
    assert_acts_equal(evaluate('ok, how many planets are bigger than the planet Mars?'), 'request_filter_compare(object=planet,property=bigger,compared_to=mars,count)')
    assert_acts_equal(evaluate('ok, how many planets there are in our solar system?'), 'request_filter_compare(object=planet,count)')
    assert_acts_equal(evaluate('how many planets are smaller than Jupiter?'), 'request_filter_compare(object=planet,property=smaller,compared_to=jupiter,count)')

def test_request_moons():
    assert_acts_equal(evaluate('ok, how many moons does the planet Mars have?'), 'request_child_objects(count,parent=mars,parent_object=planet,object=moon)')
    assert_acts_equal(evaluate('what are the moons of Jupiter?'), 'request_child_objects(parent=jupiter,parent_object=planet,object=moon)')
    assert_acts_equal(evaluate('what moons does the planet venus have?'), 'request_child_objects(parent=venus,parent_object=planet,object=moon)')

def test_request_travel_time():
    assert_acts_equal(evaluate('how long will it take us to get to the moon?'), 'request_travel_time(object=moon)')
    assert_acts_equal(evaluate('how long would it take us to get to Mars?'), 'request_travel_time(object=mars)')

def test_request_property():
    assert_acts_equal(evaluate('how big is the planet Jupiter?'), 'request_property(property=big,object=jupiter)')
    assert_acts_equal(evaluate('how big is the planet venus?'), 'request_property(property=big,object=venus)')


def test_request_object():
    assert_acts_equal(evaluate('what is Jupiter?'), 'request(object=jupiter)')

def test_humans_landed():
    assert_acts_equal(evaluate('did humans ever landed on Jupiter?'), 'request_humans_landed(object=jupiter)')
    assert_acts_equal(evaluate('didn\'t humans landed on Jupiter already?'), 'request_humans_landed(object=jupiter)')


