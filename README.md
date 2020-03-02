# ufal-dial

Minimalistic platform for dialogue system implementations.

# Installation

Clone the repo and `pip install -r requirements.txt`
The code is written in Python 3.

# Usage

The platform is based on the configuration file.
An example of such file can be found in the `conf/` directory.

To implement your pipeline, create new YAML file in the `conf/` directory and then run
`python main.py --conf conf/your_pipeline.yaml`

Essential part of the configuration is the `components` list.
You should provide one or more components that chain up to form your desired pipeline.

Each component has to inherit from the abstract class
`src.components.component.Component` and be located under the `src/components/` directory for readability.
Components also need to implement `__call__()` method which takes a dialogue state, does the work and returns the modified state.

The DialogueState object can be used as a mode of communication between components.
The object supports dictionary-like indexing and you can add your own attributes.
However, there are certain attributes that are mandatory and has to be present.
Namely:
 - `state['user']`: User utterance, this attribute will be set for you. You should not need to modify it.
 - `state['system']`: Can be set via `DialogueState::set_system_response()`. It is mandatory to set this attribute at each turn in one of your components.
 - `state['nlu']`: A dictionary of NLU annotation, doesn't have to be used.
 - `state['state_dict']'`: A dictionary representing the dialogue state, should be used to keep the persistent values.
 
Do not forget to call `DialogueState.end_dialogue()` at some point.

Each run will create a JSON file with the history of all the conversations.
You can specify this file in configuration.

For further details refer to the code.
Have fun!
