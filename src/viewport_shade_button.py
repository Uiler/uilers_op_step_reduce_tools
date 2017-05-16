import bpy
import re

from asyncore import poll


#########################################################
# Constants
#########################################################

#########################################################
# Global Variables
#########################################################
_is_closure = False
_is_draw_init = False

#########################################################
# Properties
#########################################################
def _defProperties():

    # Define Addon's Properties
    pass
    

_defProperties()


#########################################################
# Functions(Private)
#########################################################
#########################################################
# Actions
#########################################################
class toggleClosureViewportShadeButton(bpy.types.Operator):
    bl_idname = "uiler.toggleclosureviewportshadebutton"
    bl_label = "label"

    def execute(self, context):
        
        global _is_closure
        
        _is_closure = not _is_closure

        return {'FINISHED'}

#########################################################
# UI
#########################################################
def draw(layout, context):

    sp = None
    for area in bpy.context.screen.areas:
    
        if area.type == "VIEW_3D":
            sp = area.spaces[0]

    if not sp:
        return

    row = layout.row(align=True)
    row.scale_x = 1.0

    if _is_closure:
        row.operator("uiler.toggleclosureviewportshadebutton", text="", icon="DISCLOSURE_TRI_RIGHT")
    else:
        row.operator("uiler.toggleclosureviewportshadebutton", text="", icon="DISCLOSURE_TRI_DOWN")
        row.prop(context.space_data, "viewport_shade", text="", expand=True)
        
