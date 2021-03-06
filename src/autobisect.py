bl_info = {
	"name": "Auto Bisect",
	"description": "Cuts a mesh along a plane/normal to an axis.",
	"author": "brunnerh",
	"version": (1, 4),
	"blender": (2, 92, 0),
	"location": "View3D > Edit > Mesh",
	"tracker_url": "https://github.com/brunnerh/blender-utilities/issues",
	"support": "COMMUNITY",
	"category": "Mesh",
}

import bpy
from mathutils import Euler
from math import radians
from bpy import ops, types, props
from typing import List
from operator import add

class AutoBisectOperator(types.Operator):
	"""Automatically slice along a plane/normal to an axis."""
	bl_idname = "object.auto_bisect"
	bl_label = "Auto Bisect"
	bl_options = {'REGISTER', 'UNDO'}

	axis: props.EnumProperty(
		name='Axis',
		description='The cut is normal to this axis.',
		items=[
			('X', 'Normal to X', 'Normal to X Axis'),
			('Y', 'Normal to Y', 'Normal to Y Axis'),
			('Z', 'Normal to Z', 'Normal to Z Axis'),
		]
	)
	alignment: props.EnumProperty(
		name='Alignment',
		description='Defines the point through which the bisect cuts.',
		default='Object',
		items=[
			('Cursor', '3D Cursor', '3D Cursor Position'),
			('Object', 'Object Origin', 'Object Origin Position'),
			('World', 'World Origin', 'World Origin Position'),
		]
	)
	offset: props.FloatProperty(
		name='Offset',
		description='Slides the cut plane along the normal axis.',
	)
	selected_only: props.BoolProperty(
		name='Selected only',
		description='Only cuts the selected faces/edges.',
		default=False,
	)

	# Forwarded properties
	use_fill: props.BoolProperty(
		name='Fill',
		description='Fill in the cut.',
		default=False,
	)
	clear_inner: props.BoolProperty(
		name='Clear Inner',
		description='Remove geometry behind the plane.',
		default=False,
	)
	clear_outer: props.BoolProperty(
		name='Clear Inner',
		description='Remove geometry in front of the plane.',
		default=False,
	)
	threshold: props.FloatProperty(
		name='Axis Threshold',
		description='Preserves the existing geometry along the cut plane.',
		default=0.0001,
		min=0,
		precision=5,
	)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		if not self.selected_only:
			ops.mesh.select_all(action='SELECT')

		x = 1 if self.axis == 'X' else 0
		y = 1 if self.axis == 'Y' else 0
		z = 1 if self.axis == 'Z' else 0

		positions = {
			'World': (0, 0, 0),
			'Object': context.active_object.location,
			'Cursor': context.scene.cursor.location,
		}
		position = positions[self.alignment]
		offset = self.offset
		offset_vector = (offset * x, offset * y, offset * z)
		plane_co = tuple(map(add, position, offset_vector))
		plane_no = (x, y, z)

		ops.mesh.bisect(
			plane_co=plane_co,
			plane_no=plane_no,
			use_fill=self.use_fill,
			clear_inner=self.clear_inner,
			clear_outer=self.clear_outer,
			threshold=self.threshold,
		)

		return {'FINISHED'}


class AutoBisectMenu(types.Menu):
	bl_idname = "VIEW3D_MT_auto_bisect_submenu"
	bl_label = "Auto Bisect"

	def draw(self, context):
		self.layout.operator_menu_enum(AutoBisectOperator.bl_idname, property='axis')

def menu_func(self, context):
	self.layout.operator_menu_enum(AutoBisectOperator.bl_idname, property='axis')

def register():
	bpy.utils.register_class(AutoBisectOperator)
	bpy.utils.register_class(AutoBisectMenu)
	types.VIEW3D_MT_edit_mesh.append(menu_func)

def unregister():
	bpy.utils.unregister_class(AutoBisectOperator)
	bpy.utils.unregister_class(AutoBisectMenu)
	types.VIEW3D_MT_edit_mesh.remove(menu_func)

if __name__ == "__main__":
	register()