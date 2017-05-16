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
class toggleClosureKeyframeTypeButton(bpy.types.Operator):
    bl_idname = "uiler.toggleclosurekeyframetypebutton"
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

    bpy.context.scene.tool_settings.keyframe_type = prefs.keyframe_type_state

def draw(layout, context):

    row = layout.row(align=True)
    row.scale_x = 1.0
    
    if _is_closure:
        row.operator("uiler.toggleclosurekeyframetypebutton", text="", icon="DISCLOSURE_TRI_RIGHT")
    else:
        row.operator("uiler.toggleclosurekeyframetypebutton", text="", icon="DISCLOSURE_TRI_DOWN")
        
#         user_preferences = context.user_preferences
#         prefs = user_preferences.addons[__package__].preferences
#         row.prop(prefs, "keyframe_type_state", expand=True)
        row.prop(context.scene.tool_settings, "keyframe_type", expand=True, text="")
        

# from bpy.app.handlers import persistent
# 
# @persistent
# def _initForDraw(dummy):
# 
#     user_preferences = bpy.context.user_preferences
#     prefs = user_preferences.addons[__package__].preferences
#     
#     prefs.keyframe_type_state = bpy.context.scene.tool_settings.keyframe_type
# 
# bpy.app.handlers.load_post.append(_initForDraw)        


