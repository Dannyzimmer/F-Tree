from resources.libs.fcodes.fcodes.libs.classes.FBook import FBook
from resources.libs.fcodes.fcodes.libs.classes.Fcode import FcodeManager
from resources.libs.fcodes.fcodes.libs.classes.FamilyTree import FamilyTree
from resources.libs.fcodes.fcodes.libs.classes.FEntry import FEntry, FEntry_parents_booled
from resources.libs.fcodes.fcodes.libs.modules import functions as f
from tkinter.ttk import Treeview

class FBookTreeview(FBook):
    """An FBook that can be initialized from a treeview widget"""
    def __init__(self, tree_view: Treeview) -> None:
        self.tree_view = tree_view
        super().__init__('_')

    def treeview_to_fdata_line(self):
        # Initialize an empty list to store the results
        result = []
        # Iterate over the items in the treeview
        for item in self.tree_view.get_children():
            # Get the values of the first and second columns
            values = self.tree_view.item(item, 'values')
            if len(values) >= 2:
                # Append a sublist with the first and second column values
                result.append(f'{values[0]}\t{values[1]}')
        return result

    def build_DATA(self, booleanize:bool=False) -> dict:
        '''
        Return a dictionary with codes as keys and names as values:
            Ej.: {'*PMP' : FEntry(name, fcode_obj)
        file_path: path to the text file with the relatives codes.
        '''
        data = self.treeview_to_fdata_line()
        registry = {}
        for d in data:
            if len(d) > 0: 
                if d[0] != '#':
                    if booleanize == False:
                        code = d.split('\t')[0]
                    elif booleanize == True:
                        code = f.clean_fcode(d.split('\t')[0])
                    name = d.split('\t')[1]
                    if code not in registry.keys():
                        registry[code] = FEntry(name.strip(), FcodeManager(code))
        return registry
    
    def build_DATA_parents_booleanized(self) -> dict:
        data = self.treeview_to_fdata_line()
        registry = {}
        for d in data:
            if len(d) > 0: 
                if d[0] != '#':
                    original_code = d.split('\t')[0]
                    code = f.booleanize_parents(d.split('\t')[0])
                    name = d.split('\t')[1]
                    if code not in registry.keys():
                        registry[code] = FEntry_parents_booled(name=name.strip(), 
                                                            fcode=FcodeManager(code),
                                                            original_code=original_code)
        return registry

class FamilyTreeTreeview(FamilyTree):
    def __init__(self, tree_view: Treeview):
        self.tree_view = tree_view
        self.fbook = FBookTreeview(tree_view = self.tree_view)
        self.M = '#B4DBDE'
        self.F = '#E6C8E1'



    