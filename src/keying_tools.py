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

class toggleClosureKeyingtoolsUI(bpy.types.Operator):
    bl_idname = "uiler.toggleclosurekeyingtoolsui"
    bl_label = "label"

    def execute(self, context):
        
        global _is_closure
        
        _is_closure = not _is_closure

        return {'FINISHED'}

#########################################################
# UI
#########################################################
def draw(layout, context):

    row = layout.row(align=True)
    row.scale_x = 1.0
    scene = context.scene
    toolsettings = context.tool_settings
    screen = context.screen
    userprefs = context.user_preferences

    if _is_closure:
        row.operator("uiler.toggleclosurekeyingtoolsui", text="", icon="DISCLOSURE_TRI_RIGHT")
    else:
        row.operator("uiler.toggleclosurekeyingtoolsui", text="", icon="DISCLOSURE_TRI_DOWN")

        row.prop(toolsettings, "use_keyframe_insert_auto", text="", toggle=True)
        if toolsettings.use_keyframe_insert_auto:
            row.prop(toolsettings, "use_keyframe_insert_keyingset", text="", toggle=True)

            if screen.is_animation_playing and not userprefs.edit.use_keyframe_insert_available:
                subsub = row.row(align=True)
                subsub.prop(toolsettings, "use_record_with_nla", toggle=True)

#         row = layout.row(align=True)
        row.prop_search(scene.keying_sets_all, "active", scene, "keying_sets_all", text="")
        row.operator("anim.keyframe_insert", text="", icon='KEY_HLT')
        row.operator("anim.keyframe_delete", text="", icon='KEY_DEHLT')
