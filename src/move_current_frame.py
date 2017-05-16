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
def _moveCurrFrame(scn, second):
    fps = scn.render.fps
    
    movef = round(fps * second)
    
    scn.frame_current = scn.frame_current + movef

class MoveCurrFrameOne(bpy.types.Operator):
    bl_idname = "uiler.movecurrframe"
    bl_label = "label"
    
    second = bpy.props.FloatProperty()

    def execute(self, context):
        
        _moveCurrFrame(context.scene, self.second)

        return {'FINISHED'}

class toggleClosureMoveCurrentFrameButton(bpy.types.Operator):
    bl_idname = "uiler.toggleclosuremovecurrentframebutton"
    bl_label = "label"

    def execute(self, context):
        
        global _is_closure
        
        _is_closure = not _is_closure

        return {'FINISHED'}

#########################################################
# UI
#########################################################
def draw(layout, context):

    split = layout.split(0.05, align=True)
    
    if _is_closure:
        split.operator("uiler.toggleclosuremovecurrentframebutton", text="", icon="DISCLOSURE_TRI_RIGHT")
    else:
        split.operator("uiler.toggleclosuremovecurrentframebutton", text="", icon="DISCLOSURE_TRI_DOWN")
        row = split.row(align=True)
        row.scale_x = 0.5
        row.operator("uiler.movecurrframe", text="<1").second = -1.0
        row.operator("uiler.movecurrframe", text="<1/2").second = -0.5
        row.operator("uiler.movecurrframe", text="<1/4").second = -0.25
        row.operator("uiler.movecurrframe", text="<1/8").second = -0.125
        row.operator("uiler.movecurrframe", text="1/8>").second = 0.125
        row.operator("uiler.movecurrframe", text="1/4>").second = 0.25
        row.operator("uiler.movecurrframe", text="1/2>").second = 0.5
        row.operator("uiler.movecurrframe", text="1>").second = 1.0

