# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name" : "LGB",
    "author" : "Zubin Tan, Arkady Zavialov, Tomaž Roblek",
    "description" : "Unofficial Studio Lynn Blender toolkit.",
    "blender" : (3, 5, 0),
    "version" : (0, 0, 1),
    "location" : "View3D > Toolbar > LGB",
    "warning" : "",
    "category" : "Generic"
}


import bpy
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )



classes = []

bpy.types.Scene.target = bpy.props.PointerProperty(type=bpy.types.Object)
bpy.types.Scene.target2 = bpy.props.PointerProperty(type=bpy.types.Object)

        
class MotionCurveToMesh(bpy.types.Operator):
    """Transforms motion path into mesh."""
    bl_idname = "view3d.motioncurvetomesh"
    bl_label = "Bake Object"

    def execute(self, context):
        scene = context.scene
        
        newCollection = bpy.data.collections.new('Curves')
        bpy.context.scene.collection.children.link(newCollection)

        ob = scene.target2
        mp = ob.motion_path

        if mp:
            path = bpy.data.curves.new('path','CURVE')
            curve = bpy.data.objects.new('MotionPath',path)    

            newCollection.objects.link(curve)
            bpy.context.view_layer.objects.active = curve
            bpy.context.active_object.select_set(True)
            
            path.dimensions = '3D'
            spline = path.splines.new('BEZIER')
            spline.bezier_points.add(len(mp.points)-1)
            
            for i,o in enumerate(spline.bezier_points):
                o.co = mp.points[i].co
                o.handle_right_type = 'VECTOR'
                o.handle_left_type = 'VECTOR'
                

        bpy.ops.object.convert(target='MESH')

        return {"FINISHED"}

classes.append(MotionCurveToMesh)       



class BakeArmature(bpy.types.Operator):
    """Bakes armature mesh object on a desired number of frames."""
    bl_idname = "view3d.bakingoperator"
    bl_label = "Bake Object"

    def execute(self, context):
        scene = context.scene
        
        oldObject = scene.target
        text=str(oldObject) if oldObject else ""

        newCollection = bpy.data.collections.new('Slices')
        scene.collection.children.link(newCollection)
 
        #oldObject = bpy.context.active_object
        #oldObject = bpy.data.objects['Armature']
        
        frame_start = bpy.context.scene.my_tool.startFrame  
        frame_end = bpy.context.scene.my_tool.endFrame 
        step_size = bpy.context.scene.my_tool.bakeFrequency 

 
        bpy.context.scene.frame_set(frame_start)
 
        for i in range(frame_start,frame_end,step_size):
 
            bpy.context.scene.frame_set(i)
 
            newCopy = oldObject.copy()
            newCopy.data = oldObject.data.copy()
            newCopy.animation_data_clear()
 
            newCollection.objects.link(newCopy)
 
            bpy.context.view_layer.objects.active = newCopy
            bpy.ops.object.modifier_apply(modifier="Bone")
            
            for vg in newCopy.vertex_groups:
                newCopy.vertex_groups.remove(vg)
 
            world_loc = newCopy.matrix_world.to_translation()
            newCopy.parent = None       
            newCopy.matrix_world.translation = world_loc


        return {"FINISHED"}

classes.append(BakeArmature)



class LGBPanel0(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_customproppanel1"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "LGB"
    bl_label = "LGB"
    
    @classmethod
    def poll(self,context):
        return context.object is not None
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Greg's Toolkit")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        
        box = layout.box()
        box.label(text="BAKE ANIMATED OBJECT")
        
        row = box.row()
        row.prop(mytool, "startFrame")
        row = box.row()
        row.prop(mytool, "endFrame")
        row = box.row()
        row.prop(mytool, "bakeFrequency")
        row = box.row()
        row.prop_search(scene, "target", scene, "objects", text="Select Object")
        row = box.row()
        row.operator("view3d.bakingoperator")
        
        box = layout.box()
        box.label(text="MOTION PATH TO POLYLINE")
        row = box.row()
        row.prop_search(scene, "target2", scene, "objects", text="Select Object")
        row = box.row()
        row.operator("view3d.motioncurvetomesh")

classes.append(LGBPanel0)

class MyProperties(PropertyGroup):
    
    startFrame: IntProperty(
        name = "Start Frame",
        description="Start frame of baking.",
        default = 0
        )
    endFrame: IntProperty(
        name = "End Frame",
        description="End frame of baking.",
        default = 100
        )        
    bakeFrequency: IntProperty(
        name = "Bake Frequency",
        description="Define the frequency of moving armature",
        default = 10
        )
    
classes.append(MyProperties)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_tool


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.

if __name__ == "__main__":
    register()
