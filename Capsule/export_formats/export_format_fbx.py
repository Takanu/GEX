
import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.types import UILayout
from bpy.props import (
	IntProperty, 
	FloatProperty, 
	BoolProperty, 
	StringProperty, 
	PointerProperty, 
	CollectionProperty, 
	EnumProperty,
)

from .export_format import CAP_ExportFormat

class CAP_FormatData_FBX(PropertyGroup):

	instance_id: IntProperty(default=-1)

	bundle_textures: BoolProperty(
			name="Bundle Textures",
			description="If enabled, allows any textures that are packed in the .blend file and applied to an object or group that's tagged for export, to be bundled with it inside the FBX file.",
			default=False
		)

	export_object_types: EnumProperty(
		name="Object Types",
		options={'ENUM_FLAG'},
		items=(('MESH', "Mesh", ""),
			('ARMATURE', "Armature", ""),
			('CAMERA', "Camera", ""),
			('LIGHT', "Light", ""),
			('EMPTY', "Empty", ""),
			('OTHER', "Other", "Includes other mesh types like Curves and Metaballs, which are converted to meshes on export"),),
		description="Defines what kinds of objects will be exported by the FBX exporter, regardless of any other options in Capsule.",
		default={'EMPTY', 'CAMERA', 'LIGHT', 'ARMATURE', 'MESH', 'OTHER'},
	)

	global_scale: FloatProperty(
		name="Global Scale",
		description="The exported scale of the objects.",
		default=1.0
	)
	
	apply_unit_scale: BoolProperty(
		name="Apply Unit Scale",
		description="Apply Unit, Take into account current Blender units settings (if unset, raw Blender Units values are used as-is)",
		default=False
	)

	apply_scale_options: EnumProperty(
		name="Apply Scale Options",
		items=(
			('FBX_SCALE_NONE', "All Local", "Apply custom scaling and units scaling to each object transformation, FBX scale remains at 1.0."),
			('FBX_SCALE_UNITS', "FBX Units Scale", "Apply custom scaling to each object transformation, and units scaling to FBX scale."),
			('FBX_SCALE_CUSTOM', "FBX Custom Scale", "Apply custom scaling to FBX scale, and units scaling to each object transformation."),
			('FBX_SCALE_ALL', "FBX All", "Apply custom scaling and units scaling to FBX scale."),
			),
		description="Defines what kinds of objects will be exported by the FBX exporter, and will filter out objects for export even if Enable Export is ticked.",
	)

	use_space_transform: BoolProperty(
		name="Use Space Transform",
		description="Apply global space transform to the object rotations. When disabled only the axis space is written to the file and all object transforms are left as-is",
		default=False
	)

	bake_space_transform: BoolProperty(
		name="Bake Space Transform (Experimental)",
		description="Bakes the space transform of meshes from Blender into the FBX file, when the target world space does not align with the one Blender has. (WARNING - Known broken on armatures/animations, use at your own peril!)",
		default=False
	)


	axis_up: EnumProperty(
		name="Axis Up",
		description="What the Up Axis will be defined as when the model is exported.",
		items=(
			('X', 'X', ''),
			('Y', 'Y', ''),
			('Z', 'Z', ''),
			('-X', '-X', ''),
			('-Y', '-Y', ''),
			('-Z', '-Z', '')),
		default='Y',
	)



	axis_forward: EnumProperty(
		name="Axis Forward",
		description="What the Forward Axis will be defined as when the model is exported.",
		items=(
			('X', 'X', ''),
			('Y', 'Y', ''),
			('Z', 'Z', ''),
			('-X', '-X', ''),
			('-Y', '-Y', ''),
			('-Z', '-Z', '')),
		default='-Z'
	)

	convert_loose_edges: BoolProperty(
		name="Convert Loose Edges",
		description="Makes any separate edges a two-verted polygon.",
		default=False
	)

	export_normal_type: EnumProperty(
		name="Normal Export Type",
		description="Defines how mesh normals are exported.",
		items=(
			('EDGE', 'Edge', 'Writes edge smoothing data for the mesh in the FBX file.'),
			('FACE', 'Face', 'Writes face smoothing data for the mesh in the FBX file.'),
			('OFF', 'Normals Only', 'Exports the current custom normals of the model.')
			),
	)

	use_tangent_space: BoolProperty(
		name="Use Tangent Space",
		description="Exports the mesh tangent vectors,  This option will only work on objects with no n-gons (faces with more than 4 vertices), so please check beforehand!",
		default=False
	)

	use_armature_deform_only: BoolProperty(
		name="Only Include Deform Bones",
		description="Only write deforming bones (and non-deforming ones when they have deforming children)",
		default=False
	)

	add_leaf_bones: BoolProperty(
		name="Add Leaf Bones",
		description="Appends an extra bone to the end of each bone chain.",
		default=False
	)


	primary_bone_axis: EnumProperty(
		name="Primary Bone Axis",
		description="Defines the primary bone axis for the export.",
		items=(
			('X', 'X', ''),
			('Y', 'Y', ''),
			('Z', 'Z', ''),
			('-X', '-X', ''),
			('-Y', '-Y', ''),
			('-Z', '-Z', '')
			),
		default='Y'
	)

	secondary_bone_axis: EnumProperty(
		name="Secondary Bone Axis",
		description="Defines the secondary bone axis for the export.",
		items=(
			('X', 'X', ''),
			('Y', 'Y', ''),
			('Z', 'Z', ''),
			('-X', '-X', ''),
			('-Y', '-Y', ''),
			('-Z', '-Z', '')
			),
		default='X'
	)

	armature_nodetype: EnumProperty(
		name="FBX Armature NodeType",
		description="Defines the type of FBX object Blender Armatures will be represented as when exported.  Change this from Null if you're experiencing import problems in other apps, but picking anything other than null will not guarantee a successful re-import into Blender.",
		items=(
			('NULL', 'Null', "‘Null’ FBX node, similar to Blender’s Empty (default)."),
			('ROOT', 'Root', "‘Root’ FBX node, supposed to be the root of chains of bones."),
			('LIMBNODE', 'LimbNode', "‘LimbNode’ FBX node, a regular joint between two bones.")
			)
		)


	bake_anim_use_all_bones: BoolProperty(
		name="Key All Bones",
		description="If enabled, this forces the export of one key animation for all bones (required for applications like UE4).",
		default=False
	)

	bake_anim_use_nla_strips: BoolProperty(
		name="Use NLA Strips",
		description="If enabled, all non-muted NLA strips will be exported as a separated FBX AnimStack instead of global scene animation.",
		default=False
	)

	bake_anim_use_all_actions: BoolProperty(
		name="Use All Actions",
		description="If enabled, all animation actions will be exported as a separate FBX AnimStack instead of global scene animation  (note that animated objects will get all actions compatible with them, others will get no animation at all).",
		#TODO: This warning is unclear, figure out what this means and write something better.
		default=False
	)

	bake_anim_force_startend_keying: BoolProperty(
		name="Start/End Keying",
		description="If enabled, this option fully keys the start and end positions of an animation.  Use this if the exported animations playback with incorrect starting positions.",
		default=False
		)

	optimise_keyframes: BoolProperty(
		name="Optimise Keyframes",
		description="If enabled, removes double keyframes from exported animations.",
		default=False
	)

	bake_anim_step: FloatProperty(
		name="Sampling Rate",
		description="Defines how often, in frames, the export process should evaluate keyframes.",
		default=1,
		min=0.01,
		max=100,
		soft_min=0.1,
		soft_max=10
	)

	bake_anim_simplify_factor: FloatProperty(
		name="Simplify Factor",
		description="A measure for how much when exported, animations should be simplified.  Setting this value to 0 will disable simplification.  The higher the value, the greater the simplification.",
		default=1,
		min=0,
		max=100,
		soft_min=0,
		soft_max=10
	)

	# A secret fix embedded in the Unity 5 export option, to fix rotated objects.
	x_unity_rotation_fix: BoolProperty(default=False)


	def export(self, export_preset, filePath):
		"""
		Calls the FBX Export API to export the currently selected objects with the given settings.
		"""

		#print("APPLY UNIT SCALE, IS IT FUCKING ON?", self.apply_unit_scale)

		print("Exporting", "*"*70)
		bpy.ops.export_scene.fbx(
			check_existing=False,
			filepath=filePath+ ".fbx",
			filter_glob="*.fbx",
			use_selection=True,
			use_active_collection=False,
			global_scale=self.global_scale,
			apply_unit_scale=self.apply_unit_scale,
			apply_scale_options=self.apply_scale_options,
			axis_forward=self.axis_forward,
			axis_up=self.axis_up,
			use_space_transform=self.use_space_transform,
			bake_space_transform=self.bake_space_transform,
			object_types=self.export_object_types,
			use_mesh_modifiers=export_preset.apply_modifiers,
			mesh_smooth_type=self.export_normal_type,
			use_mesh_edges=self.convert_loose_edges,
			use_tspace=self.use_tangent_space,
			use_custom_props=False,  #TODO: Check what this does and if it should be enabled
			
			# Animation
			add_leaf_bones=self.add_leaf_bones,
			primary_bone_axis=self.primary_bone_axis,
			secondary_bone_axis=self.secondary_bone_axis,
			use_armature_deform_only=self.use_armature_deform_only,
			armature_nodetype=self.armature_nodetype,

			bake_anim=export_preset.export_animation,
			bake_anim_use_all_bones=self.bake_anim_use_all_bones,
			bake_anim_use_nla_strips=self.bake_anim_use_nla_strips,
			bake_anim_use_all_actions=self.bake_anim_use_all_actions,
			bake_anim_force_startend_keying=self.bake_anim_force_startend_keying,
			bake_anim_step=self.bake_anim_step,
			bake_anim_simplify_factor=self.bake_anim_simplify_factor,

			# Export Details
			path_mode='ABSOLUTE',
			embed_textures=self.bundle_textures,
			batch_mode='OFF',
			use_batch_own_dir=False,
			use_metadata=False
		
		)
	
	
	def draw_addon_preferences(self, layout, exportData, exp):
		"""
		Draws the panel that represents all the options that the export format has.
		"""

		filepresets_box = layout.column(align=True)
		filepresets_box.separator()

		export_area = filepresets_box.row(align=True)

		# left padding
		export_area.separator()

		# internal column for tabs and contents
		export_tab_area = export_area.column(align=True)
		export_tab_row = export_tab_area.row(align=True)
		export_tab_row.prop(exp, "fbx_menu_options", expand=True)
		export_tab_area.separator()
		export_tab_area.separator()

		# area for revealed export options
		export_options_area = export_tab_area.column(align=True)

		if exp.fbx_menu_options == 'Export':
			export_options = export_options_area.column(align=True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()

			export_options.prop(exportData, "bundle_textures")
			export_options.separator()

			export_options.prop(exportData, "export_object_types")
			export_options.separator()

			export_options.separator()

		if exp.fbx_menu_options == 'Transform':
			export_options = export_options_area.column(align=True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()

			export_options.prop(exportData, "global_scale")
			export_options.separator()
			export_options.prop(exportData, "apply_unit_scale")
			export_options.separator()
			export_options.separator()
			
			export_options.prop(exportData, "use_space_transform")
			export_options.prop(exportData, "bake_space_transform")
			export_options.separator()
			export_options.separator()

			export_options.prop(exportData, "axis_up")
			export_options.prop(exportData, "axis_forward")
			export_options.prop(exportData, "apply_scale_options")

			export_options.separator()

		elif exp.fbx_menu_options == 'Geometry':
			export_options = export_options_area.column(align=True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()

			export_options.prop(exportData, "convert_loose_edges")
			export_options.prop(exportData, "use_tangent_space")
			export_options.separator()
			export_options.separator()

			export_options.prop(exportData, "export_normal_type")
			export_options.separator()

			export_main.separator()

		elif exp.fbx_menu_options == 'Armature':
			export_options = export_options_area.column(align=True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()

			export_options.prop(exportData, "use_armature_deform_only")
			export_options.prop(exportData, "add_leaf_bones")
			export_options.separator()
			export_options.separator()

			export_options.prop(exportData, "primary_bone_axis")
			export_options.prop(exportData, "secondary_bone_axis")
			export_options.prop(exportData, "armature_nodetype")
			export_options.separator()


		elif exp.fbx_menu_options == 'Animation':
			export_options = export_options_area.column(align=True)
			export_options.use_property_split = True
			export_options.use_property_decorate = False  # removes animation options
			export_options.separator()

			export_options.prop(exportData, "bake_anim_use_all_bones")
			export_options.prop(exportData, "bake_anim_use_nla_strips")
			export_options.prop(exportData, "bake_anim_use_all_actions")
			export_options.prop(exportData, "bake_anim_force_startend_keying")
			export_options.prop(exportData, "optimise_keyframes")
			export_options.separator()
			export_options.separator()

			export_options.prop(exportData, "bake_anim_step")
			export_options.prop(exportData, "bake_anim_simplify_factor")
			export_options.separator()
		
		# right padding
		export_area.separator()


