import bpy
import re

from asyncore import poll


#########################################################
# Constants
#########################################################

#########################################################
# Global Variables
#########################################################

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

class SetKeyFrameTypeByButton(bpy.types.Operator):
    bl_idname = "uiler.setkeyframetypebutton"
    bl_label = "Set Keyframe Type"
    bl_options = {'REGISTER', 'UNDO'}
    
    keyfrmtype = bpy.props.StringProperty()
    
    def execute(self, context):
        
        bpy.ops.action.keyframe_type(type=self.keyfrmtype)

        return {'FINISHED'}


#########################################################
# UI
#########################################################
def draw(layout, context):

    row = layout.row(align=True)
    row.scale_x = 1.0
    row.operator("uiler.setkeyframetypebutton", text="", icon="KEYTYPE_JITTER_VEC").keyfrmtype = "JITTER"
    row.operator("uiler.setkeyframetypebutton", text="", icon="KEYTYPE_EXTREME_VEC").keyfrmtype = "EXTREME"
    row.operator("uiler.setkeyframetypebutton", text="", icon="KEYTYPE_MOVING_HOLD_VEC").keyfrmtype = "MOVING_HOLD"
    row.operator("uiler.setkeyframetypebutton", text="", icon="KEYTYPE_BREAKDOWN_VEC").keyfrmtype = "BREAKDOWN"
    row.operator("uiler.setkeyframetypebutton", text="", icon="KEYTYPE_KEYFRAME_VEC").keyfrmtype = "KEYFRAME"

