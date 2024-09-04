import json
import os

def load_json(json_file):
    with open(json_file) as f:
        return json.load(f)

class JsonManager:
    def __init__(self, json_file):
        '''Class for managing a JSON file. Attributes are the keys of the 
        given JSON. To load a different JSON file use method `load_new_json`.
        '''
        self._data = load_json(json_file)
        data = load_json(json_file)
        self._json_file = json_file
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
    
    def set_field_to_value(self, field, value):
        self._data[field] = value
    
    def write_params_to_file(self):
        with open(self._json_file, 'w') as f:
            json.dump(self._data, f, indent = 4)

class GenericManager(JsonManager):
    def __init__(self, parameter_manager: object, json_to_load: str):
        self.params = parameter_manager
        super().__init__(json_to_load)

class LangManager(GenericManager):
    def __init__(self, parameter_manager: object):
        '''Class for managing the language of the GUI. Attributes are the
        keys of the selected dictionary.
        '''
        self.params = parameter_manager
        json_to_load = self._get_language_filepath()
        super().__init__(parameter_manager, json_to_load)

    def _get_current_language(self):
        return self.params.language
    
    def _get_language_dir(self):
        return self.params.language_dir
    
    def _get_current_language_filename(self):
        language = self._get_current_language()
        lang_dir = self._get_language_dir()
        return load_json(f'{lang_dir}/filenames.json')[language]

    def load_language(self, lang_file):
        self.load_new_json(lang_file)

    def _get_language_filepath(self):
        lang_dir = self._get_language_dir()
        filename = self._get_current_language_filename()
        return lang_dir + '/' + filename

class ColorManager(GenericManager):
    '''Class for managing color of the GUI. Attributes are the keys of the
    selected dictionary.'''
    def __init__(self, parameter_manager: object):
        self.params = parameter_manager
        json_to_load = self._get_color_file()
        super().__init__(parameter_manager, json_to_load)

    def _get_color_file(self):
        return self.params.color_file

class FontManager(GenericManager):
    '''Class for managing fonts of the GUI. Attributes are the keys of the
    selected dictionary.'''
    def __init__(self, parameter_manager: object):
        self.params = parameter_manager
        self.load_new_json(self.params.font_file)

    def _add_attributes_from_dict(self, dict):
        for key in dict:
            setattr(self, key, tuple(dict[key]))

class ImageManager(GenericManager):
    '''Class for managing images of the GUI. Attributes are the keys of the
    selected dictionary.'''
    def __init__(self, parameter_manager: object):
        self.params = parameter_manager
        json_to_load = self._get_json_to_load()
        super().__init__(parameter_manager, json_to_load)

    def _get_json_to_load(self):
        return self.params.image_file

    def _add_attributes_from_dict(self, dict):
        for key in dict:
            img_path = os.path.realpath(self.params.image_dir + '/' + dict[key])
            setattr(self, key, img_path)

class ParameterManager(JsonManager):
    '''Class for managing the parameter file of the GUI. Attributes are the keys
    of the selected dictionary.'''
    def __init__(self, parameters_file):
        super().__init__(parameters_file)
    
    def write_param(self, param_name, value):
        self.set_field_to_value(param_name, value)
        self.write_params_to_file()
