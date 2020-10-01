bl_info = {
    "name": "Ray Tracing Module",
    "author": "Dimitri Croes",
    "version": (0, 0, 1),
    "blender": (2, 90, 1),
    "location": "3D View Toolbar",
    "description": "Ray based impuls response calculator",
    "warning": "",
    "doc_url": "",
    "category": "Render",
}



import bpy
import bmesh
import mathutils
import math
import os
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
                       


                       
class MyProperties(PropertyGroup):
    alpha_max: IntProperty(
        name = "Alpha Max",
        description="Maximal value for alpha in the sweep",
        default = 180,
        min = 0,
        max = 180
        )
    alpha_min: IntProperty(
        name = "Alpha Min",
        description="Minimal value for alpha in the sweep",
        default = 0,
        min = 0,
        max = 180
        )
    phi_max: IntProperty(
        name = "Phi Max",
        description="Maximal value for Phi in the sweep",
        default = 360,
        min = 0,
        max = 360
        )
    phi_min: IntProperty(
        name = "Phi Min",
        description="Minimal value for Phi in the sweep",
        default = 0,
        min = 0,
        max = 360
        )
    step_size: FloatProperty(
        name = "Step Size",
        description = "How big each step is from min to max",
        default = 1,
        min=0.000000000000001
        )   
    max_i: IntProperty(
        name = "Max bounce",
        description="Maximal amount of bounces from a wall for each ray (bigger than 100 can cause crashes)",
        default = 50,
        min = 0,
        max = 1000
        )
    speed_sound: FloatProperty(
        name = "Speed of sound",
        description = "The speed of sound in m/s",
        default = 340,
        min=0
        ) 
    my_path: StringProperty(
        name = "",
        description="Choose a directory:",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
        )

class Raytracing(Operator):
    bl_idname = "ray.raytrace"
    bl_label = "Start Raytrace"

    
    

    def get_create_object(scene):
        ob = scene.objects.get(OBJECT_NAME)
        if ob == None:
            me = bpy.data.meshes.new("Ray")
            ob = bpy.data.objects.new(OBJECT_NAME, me)
            scene.collection.objects.link(ob)
        return ob

    def execute(self, context):
        print("Starting")
        scene = bpy.context.scene
        myvar = scene.my_var
        os.remove(bpy.path.abspath(os.path.join(os.path.dirname(myvar.my_path) , "L.txt")))
        os.remove(bpy.path.abspath(os.path.join(os.path.dirname(myvar.my_path) , "D.txt")))
        EPSILON = 0.00001
        MAXIMUM_ITERATIONS = myvar.max_i
        Step=myvar.step_size
        OBJECT_NAME = 'Ray Tracer'
        L=[]
        D=[]
        #alpha=70
        #phi=90
        v=myvar.speed_sound
        for alpha in range(myvar.alpha_min,int(myvar.alpha_max/Step),1):
            alpha=alpha*Step
            for phi in range(myvar.phi_min,int(myvar.phi_max/Step),1):
                phi=phi*Step
                ob = scene.objects.get(OBJECT_NAME)
                if ob == None:
                    me = bpy.data.meshes.new("Ray")
                    ob = bpy.data.objects.new(OBJECT_NAME, me)
                    scene.collection.objects.link(ob)
                object = ob
                points = [object.location]
                A = object.location
                _, rot, _ = object.matrix_world.decompose()
                x = (math.sin(math.radians(alpha)))*(math.cos(math.radians(phi)))
                y = (math.sin(math.radians(alpha)))*(math.sin(math.radians(phi)))
                z = math.cos(math.radians(alpha))
                direction = mathutils.Vector((x, y, z))
                direction.rotate(rot)
                I=1
                d=0
                for i in range(MAXIMUM_ITERATIONS):
                    origin = points[-1] + direction * EPSILON
                    result = scene.ray_cast(scene.view_layers[0], origin=origin, direction = direction)
                    hit, location, normal, index, ob, matrix = result
                    if not hit:
                        break

                    if normal.dot(direction) < 0:
                        normal *= -1
                    di=(location - A).length
                    d=d+di
                    if ob==scene.objects.get('Listerner'):
                        d=d/v
                        L.append(I)
                        D.append(d)
                        break
                    R=float(ob.active_material.name)
                    I=I*R
                    
                    rot_dif = direction.rotation_difference(normal)
                    direction.rotate(rot_dif)
                    direction.rotate(rot_dif)
                    direction *= -1
                    points.append(location)
                    if i == MAXIMUM_ITERATIONS-1:
                        I=0
                        d=d/v
                        L.append(I)
                        D.append(d)
                        break
                    

                points.append(points[-1] + direction*10)
                bm = bmesh.new()
                [bm.verts.new(pt) for pt in points]
                bm.verts.ensure_lookup_table()
                for i in range(len(bm.verts) - 1):
                    bm.edges.new((bm.verts[i], bm.verts[i + 1]))

                bmesh.ops.transform(bm, matrix = object.matrix_world.inverted(), verts = bm.verts)
                bm.to_mesh(object.data)
                bm.free()
        print("DONE")
        f = open(bpy.path.abspath(os.path.join(os.path.dirname(myvar.my_path) , "L.txt")), "a")
        f.write(str(L))
        f.close()
        f = open(bpy.path.abspath(os.path.join(os.path.dirname(myvar.my_path) , "D.txt")), "a")
        f.write(str(D))
        f.close()
        return {'FINISHED'}

        
        
        
    #for h in bpy.app.handlers.depsgraph_update_post:
    #    bpy.app.handlers.depsgraph_update_post.remove(h) 
    #bpy.app.handlers.depsgraph_update_post.append(do_raycast)



class RayTracePanel(Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Ray Tracing Module"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        myvar = scene.my_var
        
        row=layout.row()
        row.label(text="Start raytracing with angle sweep")
        
        row=layout.row()
        row.operator("ray.raytrace")
        
        row=layout.row()
        row.label(text="Value's for alpha:")
        layout.prop(myvar, "alpha_min")
        layout.prop(myvar, "alpha_max")
        
        row=layout.row()
        row.label(text="Value's for phi:")
        layout.prop(myvar, "phi_min")
        layout.prop(myvar, "phi_max")
        
        row=layout.row()
        row.label(text="Step size:")
        layout.prop(myvar, "step_size")
        
        row=layout.row()
        row.label(text="Maximum amount of sound bounces:")
        layout.prop(myvar, "max_i")
        
        row=layout.row()
        row.label(text="Speed of sound in the room:")
        layout.prop(myvar, "speed_sound")
        
        row=layout.row()
        row.label(text="Folder where data is stored:")
        layout.prop(myvar, "my_path")
        
        row=layout.row()
        row.label(text="This Addon is made by Dimitri Croes")
        


def register():
    bpy.utils.register_class(RayTracePanel)
    bpy.utils.register_class(Raytracing)
    bpy.utils.register_class(MyProperties)
    
    bpy.types.Scene.my_var = PointerProperty(type=MyProperties)


def unregister():
    bpy.utils.unregister_class(RayTracePanel)
    bpy.utils.unregister_class(Raytracing)
    bpy.utils.unregister_class(MyProperties)
    
    del bpy.types.Scene.my_var


if __name__ == "__main__":
    register()
