
import bpy, bmesh, time
from math import *

from ..tk_utils import search as search_utils
from ..tk_utils import select as select_utils
from ..tk_utils import object_ops

# OBJECT DATA PROXY PROPERTIES
# /////////////////////////////////////////////////
# /////////////////////////////////////////////////

def FindEditableObjects(context):
    """
    Finds objects that can have their values edited.
    """
    collected = [] 
    active_obj = context.active_object

    # TODO: When I am able to fetch selected Outliner entries, remove the
    # reliance on selected objects.

    for item in context.selected_objects:
        if item.CAPObj.enable_edit is True:
            collected.append(item)
    
    # This is to ensure some parity with the Outliner.
    if active_obj.CAPObj.enable_edit is True:
        if active_obj not in collected:
            collected.append(active_obj)

    return collected

def CAP_Update_ProxyObj_EnableExport(self, context):
    """
    Updates the "Enable Export" property for all selected objects
    Note - This should only be used from the Enable Export UI tick, otherwise manually handle "Enable Export" status 
    assignment using "UpdateObjectList"
    """

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy

    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # Setup initial targets and the value state we need to change.
    collected = FindEditableObjects(context)
    value = proxy.obj_enable_export

    # Run through any collected objects to also update them.
    for item in collected:
        item.CAPObj.enable_export = value
        UpdateObjectList(context.scene, item, value)


    return None


def CAP_Update_ProxyObj_OriginPoint(self, context):
    """
    Updates the "Origin Export" property for all selected objects.
    """
    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # Setup initial targets and the value state we need to change.
    collected = FindEditableObjects(context)
    value = proxy.obj_origin_point

    # Run through the objects
    for item in collected:
        item.CAPObj.origin_point = value

    return None

def CAP_Update_ProxyObj_ObjectChildren(self, context):
    """
    Updates the "Child Objects" property for all selected objects
    """
    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # Setup initial targets and the value state we need to change.
    collected = FindEditableObjects(context)
    value = proxy.obj_object_children

    # Run through the objects
    for item in collected:
        item.CAPObj.object_children = value

    return None


def  CAP_Update_ProxyObj_LocationPreset(self, context):
    """
    Updates the "Location Preset" property for all selected objects
    """

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy

    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # Setup initial targets and the value state we need to change.
    collected = FindEditableObjects(context)
    value = proxy.obj_location_preset

    # Run through the objects
    for item in collected:
        item.CAPObj.location_preset = value

    return None

def CAP_Update_ProxyObj_ExportPreset(self, context):
    """
    Updates the "Export Preset" property for all selected objects
    """
    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
     # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # Setup initial targets and the value state we need to change.
    collected = FindEditableObjects(context)
    value = proxy.obj_export_preset

    # Run through the objects
    for item in collected:
        item.CAPObj.export_preset = value

    return None

def CAP_Update_ProxyObj_PackScript(self, context):
    """
    Updates the "Pack Script" property for all selected objects
    """
    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
     # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # Setup initial targets and the value state we need to change.
    collected = FindEditableObjects(context)
    print(collected)
    value = proxy.obj_pack_script

    # Run through the objects
    for item in collected:
        item.CAPObj.pack_script = value

    return None




# OBJECT LIST PROPERTIES
# /////////////////////////////////////////////////
# /////////////////////////////////////////////////


def UpdateObjectList(scene, object, enableExport):
    """
    Used when properties are updated outside the scope of the Export List
    to ensure that all UI elements are kept in sync.
    """
    scn = scene.CAPScn
    #print("Hey, this object is %s" % object)

    if object is None:
        return

    # Check a list entry for the object doesn't already exist.
    for item in scene.CAPScn.object_list:
        if item.object.name == object.name:
            #print("Changing", object.name, "'s export from list.'")
            item.enable_export = enableExport
            return

    # If an entry couldn't be found in the list, add it.
    if enableExport is True:
        #print("Adding", object.name, "to list.")
        entry = scn.object_list.add()
        entry.object = object
        entry.enable_export = enableExport

        object.CAPObj.in_export_list = True

    return None

def CAP_Update_FocusObject(self, context):
    """
    Focuses the camera to a particular object, ensuring the object is clearly within the camera frame.  
    """

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
            
    bpy.ops.object.select_all(action= 'DESELECT')
    select_utils.SelectObject(self.object)

    # As the context won't be correct when the icon is clicked
    # We have to find the actual 3D view and override the context of the operator

    # Deprecated in 3.2, kept just in case.
    # for area in bpy.context.screen.areas:
    #     if area.type == 'VIEW_3D':
    #         for region in area.regions:
    #             if region.type == 'WINDOW':
    #                 override = {'area': area, 
    #                             'region': region, 
    #                             'edit_object': bpy.context.edit_object, 
    #                             'scene': bpy.context.scene, 
    #                             'screen': bpy.context.screen, 
    #                             'window': bpy.context.window}

    #                 bpy.ops.view3d.view_selected(override)

    override = object_ops.Find3DViewContext()
    
    with context.temp_override(window = override['window'], area = override['area'], 
            region = override['region']):

            bpy.ops.view3d.view_selected()

    return None


def CAP_Update_SelectObject(self, context):
    """
    Selects (but doesn't focus) the given object.
    """

    bpy.ops.object.select_all(action= 'DESELECT')
    select_utils.ActivateObject(self.object)
    select_utils.SelectObject(self.object)

    return None



def CAP_Update_ObjectListExport(self, context):
    """
    Updates the "Enable Export" object status once changed from the list menu.
    Note - Do not use this in any other place apart from when an object is represented in a list.
    """

    #print("Changing Enable Export... (List)")  
    self.object.CAPObj.enable_export = self.enable_export
    
    # TODO / WARNING
    # If the object is the active selection we should really change the proxy so it fits right?
    proxy = context.scene.CAPProxy



    return None


def CAP_Update_ObjectListRemove(self, context):
    """
    Used in a list to remove an object from both the export list, while disabling it's "Enable Export" status.
    """
    #print("-----DELETING OBJECT FROM LIST-----")
    
    scn = context.scene.CAPScn
    object_list = context.scene.CAPScn.object_list

    # To avoid issues within the list, the selected list item needs to be preserved.
    backupListIndex = scn.object_list_index
    backupListLength = len(object_list)

    # TODO: Ensure it can handle deleted objects!

    # Remove it as an export candidate
    if self.object != None:
        self.object.CAPObj.enable_export = False
        self.object.CAPObj.in_export_list = False
    
    # Find the index and remove it from the list
    # TODO: There's probably a more efficient way right?
    i = None
    try:
        i = object_list.values().index(self)
        object_list.remove(i)

    except ValueError:
        return
    
    # If the index is more than the list, bring it down one
    if scn.object_list_index > i:
        scn.object_list_index -= 1

    return
                

            
