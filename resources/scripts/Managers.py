import json
import os
from customtkinter import CTkImage
from PIL import Image

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

    def refresh(self):
        self._data = load_json(self._json_file)
        self._add_attributes_from_dict(self._data)

class GenericManager(JsonManager):
    def __init__(self, parameter_manager: object, json_to_load: str):
        self.params = parameter_manager
        super().__init__(json_to_load)

    def refresh(self):
        params_path = self.params._params_path
        self._data = load_json(self._json_file)
        self._add_attributes_from_dict(self._data)
        self.params = ParameterManager(params_path)

class ParameterManager(JsonManager):
    '''Class for managing the parameter file of the GUI. Attributes are the keys
    of the selected dictionary.'''
    def __init__(self, parameters_file):
        super().__init__(parameters_file)
        self._params_path = parameters_file
    
    def write_param(self, param_name, value):
        self.set_field_to_value(param_name, value)
        self.write_params_to_file()
        self.refresh()

class LangManager(GenericManager):
    def __init__(self, parameter_manager: ParameterManager):
        '''Class for managing the language of the GUI. Attributes are the
        keys of the selected dictionary.
        '''
        self.params = parameter_manager
        language_file = self._get_language_filepath()
        super().__init__(parameter_manager, language_file)

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
        return os.path.join(lang_dir, filename)
    
    def get_available_languages(self)-> list:
        return list(load_json(self.params.available_languages_file).keys())
    
    def refresh(self):
        language_file = self._get_language_filepath()
        params_path = self.params._params_path
        self.params.refresh()
        self.params = ParameterManager(params_path)
        super().__init__(self.params, language_file)

class ColorManager(GenericManager):
    '''Class for managing color of the GUI. Attributes are the keys of the
    selected dictionary.'''
    def __init__(self, parameter_manager: ParameterManager):
        self.params = parameter_manager
        json_to_load = self._get_color_file()
        super().__init__(parameter_manager, json_to_load)

    def _get_color_file(self):
        return self.params.color_file
    
class WidgetStyleManager(GenericManager):
    '''Class for managing widgets styles of the GUI. Attributes are the keys of
    the selected dictionary.
    '''
    def __init__(self, parameter_manager: ParameterManager):
        self.params = parameter_manager
        json_to_load = self._get_widgets_file()
        super().__init__(parameter_manager, json_to_load)

    def _get_widgets_file(self):
        return self.params.widgets_style_file
    
    def _lists_to_tuples(self, dictionary: dict):
        result = {}
        for k, v in dictionary.items():
            if type(v) == list:
                result[k] = tuple(v)
            elif type(v) == dict:
                result[k] = self._lists_to_tuples(v)
            else:
                result[k] = v
        return result

    def _add_attributes_from_dict(self, dict):
        for key in dict:
            setattr(self, key, self._lists_to_tuples(dict[key]))
            print('WidgetStyleManager.', key, ' = ', self._lists_to_tuples(dict[key]))

class FontManager(GenericManager):
    '''Class for managing fonts of the GUI. Attributes are the keys of the
    selected dictionary.'''
    def __init__(self, parameter_manager: ParameterManager):
        self.params = parameter_manager
        self.load_new_json(self.params.font_file)

    def _add_attributes_from_dict(self, dict):
        for key in dict:
            setattr(self, key, tuple(dict[key]))

class ImageManager(GenericManager):
    '''Class for managing images of the GUI. Attributes are the keys of the
    selected dictionary.'''
    def __init__(self, parameter_manager: ParameterManager):
        self.params = parameter_manager
        json_to_load = self._get_json_to_load()
        super().__init__(parameter_manager, json_to_load)

    def _get_json_to_load(self):
        return self.params.image_file

    def _add_attributes_from_dict(self, dict):
        for key in dict:
            img_path = os.path.realpath(self.params.image_dir + '/' + dict[key])
            setattr(self, key, img_path)

    def get_image(self, image_name, width = 15, height = 15)-> CTkImage:
        return CTkImage(
            light_image=Image.open(self.__getattribute__(image_name)),
            size=(width, height)
            )

class RecentDBManager(GenericManager):
    def __init__(self, parameter_manager: ParameterManager):
        self.params = parameter_manager
        super().__init__(parameter_manager, self.params.recent_database_files)
        self.recent_files = self.get_recent_files()
        self.recent_paths = self.get_recent_paths()
        self.file_dic = self.get_files_dic()

    def get_recent_files(self)-> list:
        result = []
        data : dict = load_json(self.params.recent_database_files)
        for k in list(data.keys()):
            result.append(k)
        return result

    def get_recent_paths(self)-> list:
        result = []
        data : dict = load_json(self.params.recent_database_files)
        for v in list(data.values()):
            result.append(v)
        return result
    
    def get_files_dic(self)-> dict:
        result = {}
        data : dict = load_json(self.params.recent_database_files)
        for k, v in list(data.items()):
            result[k] = v
        return result
    
    def get_path_from_file(self, filename)-> str:
        if filename != '...':
            return self.file_dic[filename]
        else:
            return 'NA'
    
    def update_files_dic(self)-> None:
        self.recent_files = [os.path.basename(i) for i in self.recent_paths]
        for file, path in zip(self.recent_files, self.recent_paths):
            self.file_dic[file] = path

    def add_path_to_recent_paths(self, path)-> None:
        self.recent_paths.insert(0, path)

    def add_file_to_recent_file(self, filepath)-> None:
        self.add_path_to_recent_paths(filepath)
        if len(self.recent_paths) > int(self.params.num_recent_files):
            self.recent_paths = self.recent_paths[0:int(self.params.num_recent_files)]
        self.update_files_dic()
        with open(self.params.recent_database_files, 'w') as f:
            json.dump(self.file_dic, f, indent = 4)

class LaunchData:
    def __init__(self, parameter_manager: ParameterManager):
        self.params = parameter_manager
        self.lang_manager = LangManager(self.params)
        self.color_manager = ColorManager(self.params)
        self.font_manager = FontManager(self.params)
        self.image_manager = ImageManager(self.params)
        self.recent_manager = RecentDBManager(self.params)
        self.widget_style_manager = WidgetStyleManager(self.params)

    def refresh(self):
        self.params.refresh()
        self.lang_manager.refresh()
        self.color_manager.refresh()
        self.image_manager.refresh()
        self.widget_style_manager.refresh()

# p = ParameterManager('/home/dannyzimm/Documentos/programacion/fcodes_gui/resources/parameters.json')
# l = LangManager(p)
# pass