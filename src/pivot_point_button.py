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
class toggleClosurePoivotPointButton(bpy.types.Operator):
    bl_idname = "uiler.toggleclosurepivotpointbutton"
    bl_label = "label"

    def execute(self, context):
        
        global _is_closure
        
        _is_closure = not _is_closure

        return {'FINISHED'}

#########################################################
# UI
#########################################################
def update(self, context):
    
    user_preferences = bpy.context.user_preferences
    prefs = user_preferences.addons[__package__].preferences

    for area in bpy.context.screen.areas:
        
        if area.type == "VIEW_3D":
            area.spaces[0].pivot_point = prefs.pivot_point_state


def draw(layout, context):

#     if not _is_draw_init:
#         _initForDraw(None)

    sp = None
    for area in bpy.context.screen.areas:
    
        if area.type == "VIEW_3D":
            sp = area.spaces[0]

    if not sp:
        return

    row = layout.row(align=True)
    row.scale_x = 1.0

    if _is_closure:
        row.operator("uiler.toggleclosurepivotpointbutton", text="", icon="DISCLOSURE_TRI_RIGHT")
    else:
        row.operator("uiler.toggleclosurepivotpointbutton", text="", icon="DISCLOSURE_TRI_DOWN")

#         user_preferences = context.user_preferences
#         prefs = user_preferences.addons[__package__].preferences
#         row.prop(prefs, "pivot_point_state", expand=True)

        if sp:
            row.prop(sp, "pivot_point", text="", expand=True)
        

# from bpy.app.handlers import persistent
# 
# @persistent
# def _initForDraw(dummy):
# 
#     user_preferences = bpy.context.user_preferences
#     prefs = user_preferences.addons[__package__].preferences
#     
#     for area in bpy.context.screen.areas:
#         
#         if area.type == "VIEW_3D":
#             prefs.pivot_point_state = area.spaces[0].pivot_point
#             _is_draw_init = True
#     
# 
# bpy.app.handlers.load_post.append(_initForDraw)        
