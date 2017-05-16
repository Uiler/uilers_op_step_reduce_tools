import bpy
import re
import math

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

    pass

_defProperties()

#########################################################
# Functions(Private)
#########################################################
def _getMarkerItem(context):
    
    it = []

    max = -2**31
    min = 2**31
    for marker in context.scene.timeline_markers:

        if marker.frame > max:
            max = marker.frame

        if marker.frame < min:
            min = marker.frame
    
    try:
        padNum = str(int(math.log10(max) + 1))
    except:
        return it
    fPtn = "{0:0" + padNum + "d}"
    
    for frm in range(min, max + 1):
    
        for marker in context.scene.timeline_markers:
            
            curr = ""
            if frm == marker.frame:
                if frm == context.scene.frame_current:
                    curr = "(current)"
                it.append((str(marker.frame), fPtn.format(marker.frame) + ": " + marker.name + curr, ""))

#     return sorted(it, key=lambda name: context.scene.timeline_markers[name[0]].frame)
    
    return it

#########################################################
# Actions
#########################################################
class JumpCurrentFrameByMarkerName(bpy.types.Operator):
    bl_idname = "uiler.jumpcurrentframebymarkername"
    bl_label = "Jump by marker name"
    bl_options = {'REGISTER', 'UNDO'}
    
    def getMarkersItem(self, context):
        
        return _getMarkerItem(context)
    
    uil_jump2markers = bpy.props.EnumProperty(items = getMarkersItem, name="Markers", description="Timeline markers list.")

    def execute(self, context):
        
        for marker in context.scene.timeline_markers:
            
            if int(self.uil_jump2markers) == marker.frame:
                context.scene.frame_current = marker.frame

        return {'FINISHED'}

class JumpCurrentFrame2PreviousMarker(bpy.types.Operator):
    bl_idname = "uiler.jumpcurrentframe2previousmarker"
    bl_label = "Jump to prev marker"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        list = _getMarkerItem(context)
        scene = context.scene
        fcurrent = scene.frame_current
        
        
        for item in list:
            frm = int(item[0])
            if fcurrent > int(item[0]):
                scene.frame_current = frm

        return {'FINISHED'}

class JumpCurrentFrame2NextMarker(bpy.types.Operator):
    bl_idname = "uiler.jumpcurrentframe2nextmarker"
    bl_label = "Jump to next marker"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        list = _getMarkerItem(context)
        list.reverse()
        scene = context.scene
        fcurrent = scene.frame_current
        
        for item in list:
            frm = int(item[0])
            if fcurrent < frm:
                scene.frame_current = frm

        return {'FINISHED'}


class toggleClosureJump2TimelineMarkers(bpy.types.Operator):
    bl_idname = "uiler.toggleclosurejump2timelinemarkers"
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

    if _is_closure:
        row.operator("uiler.toggleclosurejump2timelinemarkers", text="", icon="DISCLOSURE_TRI_RIGHT")
    else:
        row.operator("uiler.toggleclosurejump2timelinemarkers", text="", icon="DISCLOSURE_TRI_DOWN")

        split = row.split(0.7, align=True)
        split.operator_menu_enum("uiler.jumpcurrentframebymarkername", "uil_jump2markers", text="Markers")
        split.operator("uiler.jumpcurrentframe2previousmarker", text="<prev")
        split.operator("uiler.jumpcurrentframe2nextmarker", text="next>")
