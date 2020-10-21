# DialMonkey 🙊

Minimalistic platform for dialogue system implementations.

# Installation

Dialmonkey requires Python 3 and [pip](https://pypi.org/project/pip/).

For a basic installation, clone the repository and run:
```
cd dialmonkey; pip install [--user] -r requirements.txt
```

If you also want to use dialmonkey as a set of libraries (e.g. import packages from it), you can
do a full in-place install of the cloned repository:
```
cd dialmonkey; pip install [--user] -e .
```
Use `--user` to install into your user directories (recommended unless you're using 
a [virtualenv](https://virtualenv.pypa.io/en/latest/) or [conda](https://docs.conda.io/en/latest/)).


# Usage

## Main: Running the Pipeline, Configuration File

The platform is based on the configuration file.
An example of such file can be found in the `conf/` directory.

To implement your pipeline, create new YAML file in the `conf/` directory and then run
`python run_dialmonkey.py --conf conf/your_pipeline.yaml`

Essential part of the configuration is the `components` list.
You should provide one or more components that chain up to form your desired pipeline.

## Your Dialogue System Components 

Each component has to inherit from the abstract class
`dialmonkey.component.Component` and be located under one of the subdirectories in the `dialmonkey/` directory  for readability
(e.g. NLU components should go under `dialmonkey/nlu/`).
Components also need to implement `__call__()` method which takes a dialogue object, does the work and returns the modified dialogue.

## The Dialogue Object -- Dialogue History

The `Dialogue` object is used as a mode of communication between components.
The object supports dictionary-like indexing and you can add your own attributes.
However, there are certain conventionally used attributes, some of them mandatory.
Namely:
 - `dialogue['user']`: Input user utterance for the current turn. This attribute will be set for you by the 
   [conversation handler](dialmonkey/conversation_handler.py). You should not need to modify it.
 - `dialogue['nlu']`: NLU annotation (a [`DA`](dialmonkey/da.py) object), doesn't have to be used.
 - `dialogue['state']'`: A dictionary representing the dialogue state, should be used to keep the persistent values
   (but isnt' mandatory).
 - `dialogue['action']`: A system action representation (a [`DA`](dialmonkey/da.py) object), doesn't have to be used.
 - `dialogue['system']`: The final system response in natural language, can be set using 
   [`Dialogue.set_system_response()`](dialmonkey/dialogue.py). It is mandatory to set this attribute at each 
   turn in one of your components.
 
Do not forget to call `Dialogue.end_dialogue()` at some point.

Each run will create a JSON file with the history of all the conversations.
You can specify this file in configuration.

## Dialogue Acts -- Meaning Representation

NLU outputs should be represented as dialogue acts (DAs) -- the class `dialmonkey.da.DA`
 is used for this purpose.

Each DA is basically a list of “dialogue act items” (DAIs) of the class `dialmonkey.da.DAI`,
which represent a triple of intent - slot - value, typically written as `intent(slot=value)`,
which is also supported by `DA`'s and `DAI`'s `str()` implementation.

* If you only use global intents (one intent per utterance), you simply set the same intent 
  for all slots in the utterance.
* If there are no slots in your utterance, you just add one `DAI` with the intent and set the 
  slot and the value to `None`.
* Sometimes only the value is `None`, e.g. `request(address)` -- here the user requests the 
  address, and we don't know the value, so the intent is `request`, the slot is `address` 
  and the value is `None`.

## Tutorial Jupyter Notebook

There is a short tutorial Jupyter notebook in [`dialmonkey101.ipynb`](dialmonkey101.ipynb). It shows:
* How to run the main pipeline (using a config file)
* How the main pipeline and each dialogue turn looks from the inside
* How to work with dialogue act objects

For further details refer to the code.
Have fun!


# Licence

© Institute of Formal and Applied Linguistics, Charles University, Prague, 2020.
Licenced under the Apache 2.0 licence.
