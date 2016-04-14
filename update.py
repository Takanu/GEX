
import bpy, bmesh, time
from .definitions import SelectObject, FocusObject, ActivateObject, CheckSuffix, CheckForTags
from math import *

def Update_EnableExport(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    scn = context.scene.CAPScn
    ui = context.scene.CAPUI

    print("Inside EnableExport (Object)")

    # If this was called from the actual UI element rather than another function,
    # we need to do stuff!
    if ui.enable_list_active == False and ui.enable_sel_active == False:
        print("Called from UI element")
        ui.enable_sel_active = True
        collected = []
        name = ""
        value = False

        # If the selection has come from the scene, get data from inside the scene
        if addon_prefs.object_multi_edit is True:
            # Acts as its own switch to prevent endless recursion
            if self == context.active_object.CAPObj:
                print("Changing Export...", context.active_object.name)

                for sel in context.selected_objects:
                    if sel.name != context.active_object.name:
                        collected.append(sel)

                # Obtain the value changed
                name = context.active_object.name
                value = self.enable_export

        # Otherwise, get information from the list
        else:
            item = scn.object_list[scn.object_list_index]
            print("Item Found:", item.name)
            name = item.name
            value = self.enable_export

        # Update the list associated with the object
        UpdateObjectList(context.scene, name, value)

        # Run through any collected objects to also update them.
        for item in collected:
            item.CAPObj.enable_export = value
            UpdateObjectList(context.scene, item.name, value)

        ui.enable_sel_active = False
        ui.enable_list_active = False

    return None


def Update_SceneOrigin(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.object_multi_edit is True:
        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.CAPObj:

            # Keep a record of the selected objects to update
            selected = []

            for sel in context.selected_objects:
                if sel.name != context.active_object.name:
                    selected.append(sel)

            # Obtain the value changed
            value = self.use_scene_origin

            # Run through the objects
            for object in selected:
                object.CAPObj.use_scene_origin = value

    return None


def Update_LocationDefault(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.object_multi_edit is True:
        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.CAPObj:
            print(context.active_object.name)

            # Keep a record of the selected objects to update
            selected = []

            for sel in context.selected_objects:
                if sel.name != context.active_object.name:
                    selected.append(sel)

            # Obtain the value changed
            value = self.location_default

            # Run through the objects
            for object in selected:
                object.CAPObj.location_default = value

    return None

def Update_ExportDefault(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.object_multi_edit is True:
        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.CAPObj:

            # Keep a record of the selected objects to update
            selected = []

            for sel in context.selected_objects:
                if sel.name != context.active_object.name:
                    selected.append(sel)

            # Obtain the value changed
            value = self.export_default

            # Run through the objects
            for object in selected:
                object.CAPObj.export_default = value

    return None

def Update_Normals(self, context):

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.object_multi_edit is True:
        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.CAPObj:

            # Keep a record of the selected objects to update
            selected = []

            for sel in context.selected_objects:
                if sel.name != context.active_object.name:
                    selected.append(sel)

            # Obtain the value changed
            value = self.normals

            # Run through the objects
            for object in selected:
                object.CAPObj.normals = value

    return None

def Update_ActionItemName(self, context):

    active = context.active_object
    print(">>> Changing Action Name <<<")
    print(self)

    if active.animation_data is not None:
        animData = active.animation_data
        print("Checking Object Animation Names...")

        if animData.action is not None:
            if animData.action.name == self.prev_name:
                animData.action.name = self.name
                self.prev_name = self.name
                return None

        for nla in active.animation_data.nla_tracks:
            print("Checking NLA...", nla, nla.name)
            if nla.name == self.prev_name:
                nla.name = self.name
                self.prev_name = self.name
                return None

    modType = {'ARMATURE'}

    for modifier in active.modifiers:
        if modifier.type in modType:
            armature = modifier.object

    if armature is not None:
        if armature.animation_data is not None:
            animData = armature.animation_data
            print("Checking Armature Animation Names...")

            if animData.action is not None:
                if animData.action.name == self.prev_name:
                    animData.action.name = self.name
                    self.prev_name = self.name
                    return None

            for nla in animData.nla_tracks:
                if nla.name == self.prev_name:
                    nla.name = self.name
                    self.prev_name = self.name
                    return None

    print("No name could be changed for action", self.prev_name, ".  Oh no!")

    return None

def Focus_Object(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    for object in context.scene.objects:
        if object.name == self.name:

            FocusObject(object)

            # As the context won't be correct when the icon is clicked
            # We have to find the actual 3D view and override the context of the operator
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            override = {'area': area, 'region': region, 'edit_object': bpy.context.edit_object, 'scene': bpy.context.scene, 'screen': bpy.context.screen, 'window': bpy.context.window}
                            bpy.ops.view3d.view_selected(override)
    return None

def Focus_Group(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    for group in bpy.data.groups:
        if group.name == self.name:

            bpy.ops.object.select_all(action='DESELECT')

            for object in group.objects:
                SelectObject(object)

            # As the context won't be correct when the icon is clicked
            # We have to find the actual 3D view and override the context of the operator
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            override = {'area': area, 'region': region, 'edit_object': bpy.context.edit_object, 'scene': bpy.context.scene, 'screen': bpy.context.screen, 'window': bpy.context.window}
                            bpy.ops.view3d.view_selected(override)

    return None

def Select_Object(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    for object in context.scene.objects:
        if object.name == self.name:

            ActivateObject(object)
            SelectObject(object)

    return None

def Select_Group(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    for group in bpy.data.groups:
        if group.name == self.name:

            #bpy.ops.object.select_all(action='DESELECT')

            for object in group.objects:
                ActivateObject(object)
                SelectObject(object)

    return None



def Update_GroupExport(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    scn = context.scene.CAPScn
    ui = context.scene.CAPUI

    print("Inside EnableExport (Object)")

    # If this was called from the actual UI element rather than another function,
    # we need to do stuff!
    if ui.enable_list_active == False and ui.enable_sel_active == False:
        print("Called from UI element")
        ui.enable_sel_active = True
        collected = []
        name = ""
        value = False

        if addon_prefs.group_multi_edit is True:
            # Acts as its own switch to prevent endless recursion
            if self == context.active_object.users_group[0].CAPGrp:
                currentGroup = None

                if context.active_object.users_group is not None:
                    currentGroup = context.active_object.users_group[0]

                collected.append(currentGroup)

                for item in context.selected_objects:
                    for group in item.users_group:
                        groupAdded = False

                        for found_group in collected:
                            if found_group.name == group.name:
                                groupAdded = True

                        if groupAdded == False:
                            collected.append(group)

                collected.remove(currentGroup)
                name = currentGroup.name
                value = self.export_group

        # Otherwise, get information from the list
        else:
            item = scn.group_list[scn.group_list_index]
            print("Item Found:", item.name)
            name = item.name
            value = self.enable_export

        # Obtain the value changed
        UpdateGroupList(context.scene, name, value)

        # Run through the objects
        for group in collected:
            group.CAPGrp.export_group = value
            UpdateGroupList(context.scene, group.name, self.export_group)

        ui.enable_sel_active = False
        ui.enable_list_active = False

    return None


def Update_GroupRootObject(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.group_multi_edit is True:
        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.users_group[0].CAPGrp:
            currentGroup = None
            if context.active_object.users_group is not None:
                currentGroup = context.active_object.users_group[0]

            groups_found = []
            groups_found.append(currentGroup)

            for item in context.selected_objects:
                for group in item.users_group:
                    groupAdded = False

                    for found_group in groups_found:
                        if found_group.name == group.name:
                            groupAdded = True

                    if groupAdded == False:
                        print("")
                        groups_found.append(group)

            groups_found.remove(currentGroup)

            # Obtain the value changed
            value = currentGroup.CAPGrp.root_object

            # Run through the objects
            for group in groups_found:
                group.CAPGrp.root_object = value

    return None

def Update_GroupExportDefault(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.group_multi_edit is True:
        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.users_group[0].CAPGrp:
            currentGroup = None
            if context.active_object.users_group is not None:
                currentGroup = context.active_object.users_group[0]

            groups_found = []
            groups_found.append(currentGroup)

            for item in context.selected_objects:
                for group in item.users_group:
                    groupAdded = False

                    for found_group in groups_found:
                        if found_group.name == group.name:
                            groupAdded = True

                    if groupAdded == False:
                        print("")
                        groups_found.append(group)

            groups_found.remove(currentGroup)

            # Obtain the value changed
            value = currentGroup.CAPGrp.export_default

            # Run through the objects
            for group in groups_found:
                group.CAPGrp.export_default = value

    return None

def Update_GroupLocationDefault(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.group_multi_edit is True:
        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.users_group[0].CAPGrp:
            currentGroup = None
            if context.active_object.users_group is not None:
                currentGroup = context.active_object.users_group[0]

            groups_found = []
            groups_found.append(currentGroup)

            for item in context.selected_objects:
                for group in item.users_group:
                    groupAdded = False

                    for found_group in groups_found:
                        if found_group.name == group.name:
                            groupAdded = True

                    if groupAdded == False:
                        print("")
                        groups_found.append(group)

            groups_found.remove(currentGroup)

            # Obtain the value changed
            value = currentGroup.CAPGrp.location_default

            # Run through the objects
            for group in groups_found:
                group.CAPGrp.location_default = value

    return None

def Update_GroupNormals(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if addon_prefs.group_multi_edit is True:
        # Acts as its own switch to prevent endless recursion
        if self == context.active_object.users_group[0].CAPGrp:
            currentGroup = None
            if context.active_object.users_group is not None:
                currentGroup = context.active_object.users_group[0]

            groups_found = []
            groups_found.append(currentGroup)

            for item in context.selected_objects:
                for group in item.users_group:
                    groupAdded = False

                    for found_group in groups_found:
                        if found_group.name == group.name:
                            groupAdded = True

                    if groupAdded == False:
                        print("")
                        groups_found.append(group)

            groups_found.remove(currentGroup)

            # Obtain the value changed
            value = currentGroup.CAPGrp.normals

            # Run through the objects
            for group in groups_found:
                group.CAPGrp.normals = value

    return None

def Update_ObjectItemName(self, context):

    print("Finding object name to replace")

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    ui = context.scene.CAPUI

    # Set the name of the item to the group name
    for object in context.scene.objects:
        if object.name == self.prev_name:

            print("Found object name ", object.name)
            object.name = self.name
            self.prev_name = object.name

            print("object Name = ", object.name)
            print("List Name = ", self.name)
            print("Prev Name = ", self.prev_name)

        return None

def Update_ObjectItemExport(self, context):

    print("Changing Enable Export... (List)")

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    ui = context.scene.CAPUI
    ui.enable_list_active = True

    if ui.enable_sel_active == False:
        print("Rawr")
        # Set the name of the item to the group name
        for item in context.scene.objects:
            if item.name == self.name:
                print("Found object name ", item.name)
                item.CAPObj.enable_export = self.enable_export

    ui.enable_sel_active = False
    ui.enable_list_active = False
    return None

def Update_GroupItemName(self, context):

    # Set the name of the item to the group name
    for group in bpy.data.groups:
        print("Finding group name to replace")
        if group.name == self.prev_name:

            print("Found group name ", group.name)
            group.name = self.name
            self.prev_name = group.name

            print("Group Name = ", group.name)
            print("List Name = ", self.name)
            print("Prev Name = ", self.prev_name)

    return None

def Update_GroupItemExport(self, context):

    print("Changing Enable Export... (List)")

    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences
    ui = context.scene.CAPUI
    ui.enable_list_active = True

    if ui.enable_sel_active == False:

        # Set the name of the item to the group name
        for group in bpy.data.groups:
            print("Finding group name to replace")
            if group.name == self.name:
                print("Found object name ", group.name)
                group.CAPGrp.export_group = self.enable_export

    ui.enable_sel_active = False
    ui.enable_list_active = False

    return None

def Update_ObjectListSelect(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if self.object_list_index != -1:
        print("Selection in list, turning off multi edit...")
        addon_prefs.object_multi_edit = False

def Update_GroupListSelect(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__package__].preferences

    if self.group_list_index != -1:
        print("Selection in list, turning off multi edit...")
        addon_prefs.group_multi_edit = False

def Update_ObjectRemoveFromList(self, context):
    print("-----DELETING OBJECT FROM LIST-----")
    i = 0
    ui = context.scene.CAPUI
    scn = context.scene.CAPScn
    # To avoid issues within the list, the selected list item needs to be preserved.
    backupListIndex = scn.object_list_index

    # Search through the object list to find a matching name
    for item in scn.object_list:
        if item.name == self.name:
            # Search through scene objects to untick export
            for sceneObj in context.scene.objects:
                if sceneObj.name == self.name:
                    print("Deleting", sceneObj.name, "from the list.")
                    ui.enable_list_active = True

                    sceneObj.CAPObj.enable_export = False
                    context.scene.CAPScn.object_list.remove(i)
                    if backupListIndex != 0:
                        scn.object_list_index = backupListIndex - 1

                    ui.enable_sel_active = False
                    ui.enable_list_active = False
                    return
        i += 1


def Update_GroupRemoveFromList(self, context):
    print("-----DELETING GROUP FROM LIST-----")
    i = 0
    ui = context.scene.CAPUI
    scn = context.scene.CAPScn
    # To avoid issues within the list, the selected list item needs to be preserved.
    backupListIndex = scn.group_list_index

    for item in scn.group_list:
        if item.name == self.name:
            # Search through scene groups to untick export
            for sceneGroup in bpy.data.groups:
                if sceneGroup.name == self.name:
                    print("Deleting", sceneGroup.name, "from the list.")
                    ui.enable_list_active = True

                    sceneGroup.CAPGrp.export_group = False
                    context.scene.CAPScn.group_list.remove(i)
                    if backupListIndex != 0:
                        scn.group_list_index = backupListIndex - 1

                    ui.enable_sel_active = False
                    ui.enable_list_active = False
                    return
        i += 1


def UpdateObjectList(scene, name, enableExport):

    ui = scene.CAPUI
    scn = scene.CAPScn

    # Check a list entry for the object doesn't already exist.
    for item in scene.CAPScn.object_list:
        if item.name == name:
            print("Changing", name, "'s export from list.'")
            item.enable_export = enableExport
            return

    if enableExport is True:
        print("Adding", name, "to list.")
        entry = scn.object_list.add()
        entry.name = name
        entry.prev_name = name
        entry.enable_export = enableExport

def UpdateGroupList(scene, name, enableExport):

    ui = scene.CAPUI
    scn = scene.CAPScn

    # Check a list entry for the group doesn't already exist.
    for item in scene.CAPScn.group_list:
        if item.name == name:
            print("Changing", name, "'s export from list.'")
            item.enable_export = enableExport
            return

    if enableExport is True:
        print("Adding", name, "to list.")
        entry = scn.group_list.add()
        entry.name = name
        entry.prev_name = name
        entry.enable_export = enableExport
