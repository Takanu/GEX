
import bpy
from mathutils import Vector
from .object_ops import SwitchObjectMode, Find3DViewContext
from .select import FocusObject, SelectObject, ActivateObject

def MoveAllFailsafe(context, move_target, destination):
    """
    Moves every object in the scene safely.
    BLENDER 2.8 - This also uses a region to ensure that it moves in a 3D View region that hasnt been deallocated.
    """
    # ///////////////////////////////
    # WARNING - WARNING - WARNING - WARNING - WARNING - WARNING
    # The context override is known to crash only when testing.
    # Under normal circumstances this function is completely safe.
    # ///////////////////////////////

    # This doesnt need the cursor, and will ensure nothing is animated
	# in the process

    location = [0.0, 0.0, 0.0]
    location[0] = destination[0]
    location[1] = destination[1]
    location[2] = destination[2]

    # Prevent auto keyframing and location lock from being active
    auto_key = context.scene.tool_settings.use_keyframe_insert_auto
    lock_location_record = move_target.lock_location

    context.scene.tool_settings.use_keyframe_insert_auto = False
    move_target.lock_location = (False, False, False)

    # Save the current cursor location
    cursor_loc = bpy.data.scenes[context.scene.name].cursor.location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    override = Find3DViewContext()
    with context.temp_override(area = override['area']):

        # Calculate the translation vector using the 3D cursor
        bpy.ops.object.select_all(action = 'DESELECT')
        FocusObject(move_target)

        bpy.ops.view3d.snap_cursor_to_selected()

        root_location = (0.0, 0.0, 0.0)
        root_location = context.scene.cursor.location

        # Calculate the movement difference
        location_diff = Vector((0.0, 0.0, 0.0))
        location_diff.x = (location[0] - root_location[0])
        location_diff.y = (location[1] - root_location[1])
        location_diff.z = (location[2] - root_location[2])

        bpy.ops.object.select_all(action= 'SELECT')

        ActivateObject(move_target)

        previous_mode = bpy.context.active_object.mode

        # This form of translation is required in order to avoid any issues related to parent/child
        # and constraints when moving objects individually.

        bpy.ops.transform.translate(
            value = location_diff,
            constraint_axis = (False, False, False),
            orient_type = 'GLOBAL',
            mirror = False,
            use_proportional_edit = False,
            snap = False,
            release_confirm = False,
        )

        bpy.ops.object.mode_set(mode = previous_mode)

    # Position the cursor back to it's original location
    bpy.data.scenes[bpy.context.scene.name].cursor.location = previous_cursor_loc

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = auto_key
    move_target.lock_location = lock_location_record

    print('Move finished.')

def MoveObjectFailsafe(target, context, location):
    """
    Safely moves the given object to the given location.  Will ensure nothing is animated or screwed up in the process.
    WORKAROUND FOR BLENDER 2.8 CRASH FUNTIMES.
    """

	# This doesnt need the cursor, and will ensure nothing is animated
	# in the process

    #print(">>>>>> Moving Object <<<<<<")

    override = Find3DViewContext()

    with context.temp_override(window = override['window'], area = override['area'],
            region = override['region']):

        copy_location = Vector((location[0], location[1], location[2]))

        # Prevent auto keyframing from being active
        auto_key = context.scene.tool_settings.use_keyframe_insert_auto
        lock_transform = target.lock_location

        context.scene.tool_settings.use_keyframe_insert_auto = False
        target.lock_location = (False, False, False)

        # Save the current cursor location
        cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor.location
        previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

        # This line is actually super-important, not sure why though...
        # FocusObject should fill the role of deselection...
        bpy.ops.object.select_all(action= 'DESELECT')

        # Calculate the translation vector using the 3D cursor
        FocusObject(target)
        bpy.ops.view3d.snap_cursor_to_selected()
        translation_loc = Vector((0.0, 0.0, 0.0))

        translation_loc = bpy.context.scene.cursor.location
        previous_mode = bpy.context.active_object.mode

        # Calculate the movement difference
        location_diff = copy_location - translation_loc

        # NEW Translate
        bpy.ops.transform.translate(
            value = location_diff,
            constraint_axis = (False, False, False),
            orient_type = 'GLOBAL',
            mirror = False,
            use_proportional_edit = False,
            snap = False,
            release_confirm = False,
        )

        bpy.ops.object.mode_set(mode=previous_mode)

        # Position the cursor back to it's original location
        bpy.data.scenes[bpy.context.scene.name].cursor.location = previous_cursor_loc

        # Restore the previous setting
        context.scene.tool_settings.use_keyframe_insert_auto = auto_key
        target.lock_location = lock_transform

def MoveBone(target, bone, context, location):
    """
    Safely moves the given bone to the given location.  Will ensure nothing is animated or screwed up in the process.
    """

	# This doesnt need the cursor, and will ensure nothing is animated
	# in the process

    #print(">>> Moving Object <<<")

    copy_location = Vector((0.0, 0.0, 0.0))
    copy_location[0] = location[0]
    copy_location[1] = location[1]
    copy_location[2] = location[2]

    # Prevent auto keyframing from being active
    auto_key = context.scene.tool_settings.use_keyframe_insert_auto
    lock_transform = target.lock_location

    context.scene.tool_settings.use_keyframe_insert_auto = False
    target.lock_location = (False, False, False)

    # Save the current cursor location
    cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor.location
    previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

    # This line is actually super-important, not sure why though...
    # FocusObject should fill the role of deselection...
    bpy.ops.object.select_all(action= 'DESELECT')

    # Calculate the translation vector using the 3D cursor
    prevMode = SwitchObjectMode('POSE', target)
    bpy.data.objects[target.name].data.bones.active = bpy.data.objects[target.name].pose.bones[bone.name].bone
    bpy.ops.view3d.snap_cursor_to_selected()
    translation_loc = Vector((0.0, 0.0, 0.0))

    #print("RAWR")
    translation_loc = bpy.context.scene.cursor.location

    # for area in context.screen.areas:
    #     if area.type == 'VIEW_3D':
    #         translation_loc = area.spaces[0].cursor.location

    #print(translation_loc)

    # Calculate the movement difference
    location_diff = copy_location - cursor.location

    bpy.ops.transform.translate(
        value=location_diff,
        constraint_axis= (False, False, False),
        orient_type = 'GLOBAL',
        mirror= False,
        use_proportional_edit= False,
        snap= False,
        snap_target= 'CLOSEST',
        snap_point= (0.0, 0.0, 0.0),
        snap_align= False,
        snap_normal= (0.0, 0.0, 0.0),
        gpencil_strokes= False,
        texture_space= False,
        remove_on_cancel= False,
        release_confirm= False)

    #print("Object", bone.name, "moved.... ", bone.location)

    SwitchObjectMode(prevMode, target)

    # Position the cursor back to it's original location
    #bpy.data.scenes[bpy.context.scene.name].cursor.location = previous_cursor_loc

    # Restore the previous setting
    #context.scene.tool_settings.use_keyframe_insert_auto = auto_key
    #target.lock_location = lock_transform


def RotateObjectSafe(target, context, rotation, forward):
    """
    Safely rotates the given objects with the given rotation.  Will ensure nothing is animated or screwed up in the process.
    """

    # Prevent auto keyframing and location lock from being active
    auto_key = context.scene.tool_settings.use_keyframe_insert_auto
    context.scene.tool_settings.use_keyframe_insert_auto = False

    FocusObject(target)

    # Obtain the current rotation mode
    order = target.rotation_mode

    # Sort out how we're going to filter through the rotation order
    rotationOrder = []
    rotationComponents = []
    axisX = [0, (1.0, 0.0, 0.0), (True, False, False)]
    axisY = [1, (0.0, 1.0, 0.0), (False, True, False)]
    axisZ = [2, (0.0, 0.0, 1.0), (False, False, True)]

    if order == 'ZYX':
        if forward is True:
            rotationComponents = [axisZ, axisY, axisX]
        else:
            rotationComponents = [axisX, axisY, axisZ]
    elif order == 'ZXY':
        if forward is True:
            rotationComponents = [axisZ, axisX, axisY]
        else:
            rotationComponents = [axisY, axisX, axisZ]
    elif order == 'YZX':
        if forward is True:
            rotationComponents = [axisY, axisZ, axisX]
        else:
            rotationComponents = [axisX, axisZ, axisY]
    elif order == 'YXZ':
        if forward is True:
            rotationComponents = [axisY, axisX, axisZ]
        else:
            rotationComponents = [axisZ, axisX, axisY]
    elif order == 'XZY':
        if forward is True:
            rotationComponents = [axisX, axisZ, axisY]
        else:
            rotationComponents = [axisY, axisZ, axisX]
    elif order == 'XYZ':
        if forward is True:
            rotationComponents = [axisX, axisY, axisZ]
        else:
            rotationComponents = [axisZ, axisY, axisX]


    # Set the pivot to be the target object
    backupPivot = 'CURSOR'
    backupAlign = False
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            backupPivot = area.spaces[0].pivot_point
            backupAlign = area.spaces[0].use_pivot_point_align
            area.spaces[0].pivot_point = 'ACTIVE_ELEMENT'
            area.spaces[0].use_pivot_point_align = False

    # Rotate in Euler order
    for i, item in enumerate(rotationComponents):
        if rotation[item[0]] != 1:

            bpy.ops.transform.rotate(
                value=rotation[item[0]],
                axis=item[1],
                constraint_axis=item[2],
                orient_type = 'GLOBAL',
                release_confirm= True
                )

    # Restore the pivot
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].pivot_point = backupPivot
            area.spaces[0].use_pivot_point_align = backupAlign

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = auto_key




def RotateAll(target, context, rotation, constraintAxis):
    """
    ???
    """
    # Prevent auto keyframing and location lock from being active
    auto_key = context.scene.tool_settings.use_keyframe_insert_auto
    context.scene.tool_settings.use_keyframe_insert_auto = False

    bpy.ops.object.select_all(action= 'SELECT')
    ActivateObject(target)

    # Set the pivot to be the target object
    backupPivot = 'CURSOR'
    backupAlign = False
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            backupPivot = area.spaces[0].pivot_point
            backupAlign = area.spaces[0].use_pivot_point_align
            area.spaces[0].pivot_point = 'ACTIVE_ELEMENT'
            area.spaces[0].use_pivot_point_align = False

    bpy.ops.transform.rotate(
        value=radians(rotation),
        axis= (1.0, 1.0, 1.0),
        constraint_axis=constraintAxis,
        orient_type = 'GLOBAL',
        release_confirm= True
        )

    # Restore the pivot
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].pivot_point = backupPivot
            area.spaces[0].use_pivot_point_align = backupAlign

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = auto_key

def RotateAllSafe(target, context, rotation, forward):
    """
    ???
    """

    # Prevent auto keyframing and location lock from being active
    auto_key = context.scene.tool_settings.use_keyframe_insert_auto
    context.scene.tool_settings.use_keyframe_insert_auto = False

    bpy.ops.object.select_all(action= 'SELECT')
    ActivateObject(target)

    # Obtain the current rotation mode
    order = target.rotation_mode

    # Sort out how we're going to filter through the rotation order
    rotationOrder = []
    rotationComponents = []
    axisX = [0, (1.0, 0.0, 0.0), (True, False, False)]
    axisY = [1, (0.0, 1.0, 0.0), (False, True, False)]
    axisZ = [2, (0.0, 0.0, 1.0), (False, False, True)]

    if order == 'ZYX':
        if forward is True:
            rotationComponents = [axisZ, axisY, axisX]
        else:
            rotationComponents = [axisX, axisY, axisZ]
    elif order == 'ZXY':
        if forward is True:
            rotationComponents = [axisZ, axisX, axisY]
        else:
            rotationComponents = [axisY, axisX, axisZ]
    elif order == 'YZX':
        if forward is True:
            rotationComponents = [axisY, axisZ, axisX]
        else:
            rotationComponents = [axisX, axisZ, axisY]
    elif order == 'YXZ':
        if forward is True:
            rotationComponents = [axisY, axisX, axisZ]
        else:
            rotationComponents = [axisZ, axisX, axisY]
    elif order == 'XZY':
        if forward is True:
            rotationComponents = [axisX, axisZ, axisY]
        else:
            rotationComponents = [axisY, axisZ, axisX]
    elif order == 'XYZ':
        if forward is True:
            rotationComponents = [axisX, axisY, axisZ]
        else:
            rotationComponents = [axisZ, axisY, axisX]


    # Set the pivot to be the target object
    backupPivot = 'CURSOR'
    backupAlign = False
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            backupPivot = area.spaces[0].pivot_point
            backupAlign = area.spaces[0].use_pivot_point_align
            area.spaces[0].pivot_point = 'ACTIVE_ELEMENT'
            area.spaces[0].use_pivot_point_align = False

    # Rotate in Euler order
    for i, item in enumerate(rotationComponents):
        if rotation[item[0]] != 1:

            bpy.ops.transform.rotate(
                value=rotation[item[0]],
                axis=item[1],
                constraint_axis=item[2],
                orient_type = 'GLOBAL',
                release_confirm= True
                )

    # Restore the pivot
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].pivot_point = backupPivot
            area.spaces[0].use_pivot_point_align = backupAlign

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = auto_key

def ScaleAll(context, scale, constraintAxis):
    """
    ???
    """
    # Prevent auto keyframing and location lock from being active
    auto_key = context.scene.tool_settings.use_keyframe_insert_auto
    context.scene.tool_settings.use_keyframe_insert_auto = False

    bpy.ops.object.select_all(action= 'SELECT')

    bpy.ops.transform.resize(
        value=scale,
        constraint_axis=constraintAxis,
        orient_type = 'GLOBAL',
        mirror= False,
        proportional= 'DISABLED',
        proportional_edit_falloff= 'SMOOTH',
        proportional_size= 1.0,
        snap= False,
        snap_target= 'CLOSEST',
        snap_point= (0.0, 0.0, 0.0),
        snap_align= False,
        snap_normal= (0.0, 0.0, 0.0),
        gpencil_strokes= False,
        texture_space= False,
        remove_on_cancel= False,
        release_confirm= False
        )

    # Restore the previous setting
    context.scene.tool_settings.use_keyframe_insert_auto = auto_key