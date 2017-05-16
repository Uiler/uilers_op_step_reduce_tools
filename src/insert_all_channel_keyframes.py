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

class InsertAllChannelsKeyframesAtDopesheet(bpy.types.Operator):
    bl_idname = "uiler.insertallchannelskeyframesatdopesheet"
    bl_label = "Insert Keyframes(All Channels)"
    bl_description = "Insert Keyframes(All Channels)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        bpy.ops.action.keyframe_insert(type="ALL")

        return {'FINISHED'}


#########################################################
# UI
#########################################################
        
def draw(layout, context):
    
    layout.separator()

    row = layout.row(align=True)
    row.scale_x = 1.0
    row.operator("uiler.insertallchannelskeyframesatdopesheet", text="", icon="REC")


