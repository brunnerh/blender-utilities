bl_info = {
	"name": "Auto Knife",
	"description": "Cuts a mesh along a plane/normal to an axis.",
	"author": "brunnerh",
	"version": (1, 1),
	"blender": (2, 90, 1),
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

class AutoKnifeOperator(types.Operator):
	"""Automatically slice along an axis."""
	bl_idname = "object.auto_knife"
	bl_label = "Auto Knife"
	bl_options = {'REGISTER', 'UNDO'}

	axis: props.EnumProperty(
		name='Axis',
		description='The cut is normal to this axis.',
		items=[
			('X', 'Normal to X', 'Normal to X Axis'),
			('Y', 'Normal to Y', 'Normal to Y Axis'),
			('Z', 'Normal to Z', 'Normal to Z Axis')
		]
	)
	# TODO: offset is buggy
	# offset: props.FloatProperty(
	# 	name='Offset',
	# 	description='Slides the cut along the axis.',
	# )

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		undos = []

		flatten = lambda t: [item for sublist in t for item in sublist]

		end = 10000
		# offset = self.offset
		offset = 0
		axis_data_set = {
			'X': {
				'line': [(offset, 0, end), (offset, 0, -end)],
				'view_location': [0, 100, 0],
				'view_rotation': Euler((0, 0, radians(-90))),
			},
			'Y': {
				'line': [(end, offset, 0), (-end, offset, 0)],
				'view_location': [0, 0, 100],
				'view_rotation': Euler((0, 0, 0)),
			},
			'Z': {
				'line': [(0, end, offset), (0, -end, offset)],
				'view_location': [100, 0, 0],
				'view_rotation': Euler((0, radians(-90), 0)),
			},
		}
		axis_data = axis_data_set[self.axis]

		def add_knife():
			path = bpy.data.curves.new('knife', 'CURVE')
			path.dimensions = '3D'

			coords = axis_data['line']
			spline = path.splines.new('POLY')
			spline.points.add(len(coords))
			for i, coord in enumerate(coords):
				x, y, z = coord
				spline.points[i].co = (x, y, z, 1)

			pathObj = bpy.data.objects.new('knife', path)

			context.scene.collection.objects.link(pathObj)
			pathObj.select_set(True)

			def undo():
				context.scene.collection.objects.unlink(pathObj)
			
			undos.append(undo)

		def change_view():
			windows = bpy.data.window_managers[0].windows
			areas = [x for x in flatten([window.screen.areas for window in windows]) if x.type == 'VIEW_3D']
			spaces = [x for x in flatten([area.spaces for area in areas]) if x.type == 'VIEW_3D']
			for space in spaces:
				region = space.region_3d

				original_perspective = region.view_perspective
				original_location = [x for x in region.view_location]
				original_rotation = [x for x in region.view_rotation]

				region.view_perspective = 'ORTHO'
				region.view_location = axis_data['view_location']
				r = axis_data['view_rotation'].to_quaternion()
				region.view_rotation = [r.x, r.y, r.z, r.w]
				region.update()

				def undo():
					region.view_perspective = original_perspective
					region.view_location = original_location
					region.view_rotation = original_rotation
					region.update()

				undos.append(undo)

		def project():
			ops.object.mode_set(mode='EDIT')
			ops.mesh.knife_project(cut_through=True)

		try:
			add_knife()
			change_view()
			project()
		finally:
			for undo in reversed(undos):
			 	undo()

		return {'FINISHED'}


class AutoKnifeMenu(types.Menu):
	bl_idname = "VIEW3D_MT_auto_knife_submenu"
	bl_label = "Auto Knife"

	def draw(self, context):
		self.layout.operator_menu_enum(AutoKnifeOperator.bl_idname, property='axis')

def menu_func(self, context):
	self.layout.operator_menu_enum(AutoKnifeOperator.bl_idname, property='axis')

def register():
	bpy.utils.register_class(AutoKnifeOperator)
	bpy.utils.register_class(AutoKnifeMenu)
	types.VIEW3D_MT_edit_mesh.append(menu_func)

def unregister():
	bpy.utils.unregister_class(AutoKnifeOperator)
	bpy.utils.unregister_class(AutoKnifeMenu)
	types.VIEW3D_MT_edit_mesh.remove(menu_func)

if __name__ == "__main__":
	register()