import json

def load_json(json_file):
    with open(json_file) as f:
        return json.load(f)

class JsonManager:
    def __init__(self, json_file):
        '''Class for managing a JSON file. Attributes are the keys of the 
        given JSON. To load a different JSON file use method `load_new_json`.
        '''
        data = load_json(json_file)
        self._add_attributes_from_dict(data)

    def _remove_attributes(self):
        for attr in list(self.__dict__.keys()):
            delattr(self, attr)
    
    def _add_attributes_from_dict(self, dict):
        for key in dict:
            setattr(self, key, dict[key])

    def load_new_json(self, json_file):
        data = load_json(json_file)
        self._remove_attributes()
        self._add_attributes_from_dict(data)

class LangManager(JsonManager):
    def __init__(self, language, parameters_file):
        '''Class for managing the language of the GUI. Attributes are the
        keys of the selected dictionary.
        '''
        self._parameters_file = parameters_file
        super().__init__(self._get_language_filepath(language))

    def load_language(self, lang_file):
        self.load_new_json(lang_file)

    def _get_language_filepath(self, language):
        lang_dir = load_json(self._parameters_file)['language_dir']
        filename = load_json(f'{lang_dir}/filenames.json')[language]
        return lang_dir + '/' + filename

class ColorManager(JsonManager):
    '''Class for managing color of the GUI. Attributes are the keys of the
    selected dictionary.'''
    def __init__(self, color_file):
        super().__init__(color_file)

class FontManager(JsonManager):
    '''Class for managing fonts of the GUI. Attributes are the keys of the
    selected dictionary.'''
    def __init__(self, font_file):
        self.load_new_json(font_file)

    def _add_attributes_from_dict(self, dict):
        for key in dict:
            setattr(self, key, tuple(dict[key]))

class ParameterManager(JsonManager):
    '''Class for managing the parameter file of the GUI. Attributes are the keys
    of the selected dictionary.'''
    def __init__(self, parameters_file):
        super().__init__(parameters_file)