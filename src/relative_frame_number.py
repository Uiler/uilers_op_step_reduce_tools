import bpy
import re
import math

from asyncore import poll
from . import common
import bgl

#########################################################
# Constants
#########################################################
_FUNCTION_NAME = "Relative frame number from start frame"

#########################################################
# Global Variables
#########################################################
_is_closure = False
_is_render = False

#########################################################
# Functions(Private)
#########################################################
def updateRelative(self, context):
    
    _updateRelative(context)

def _updateRelative(context):

    if common.isActiveAddonFunctionByName(_FUNCTION_NAME) and not _is_render:
        scene = context.scene
        propgrp = scene.uil_op_step_reduce_tools_propgrp
        origin_offset = 0
        if not propgrp.uil_relative_frame_number_origin:
            origin_offset = 1
        
        if scene.frame_start > 0:
            scene.frame_current = scene.frame_start + propgrp.uil_relative_frame_number_current_frame - 1 + origin_offset
        else:
            offset = 1 + abs(scene.frame_start)
            scene.frame_current = scene.frame_start + propgrp.uil_relative_frame_number_current_frame - offset + origin_offset

def updateOrigin(self, context):
    
    pass

#########################################################
# Actions
#########################################################
class toggleClosureRelativeFrameNumberUI(bpy.types.Operator):
    bl_idname = "uiler.toggleclosurerelativeframenumberui"
    bl_label = "label"

    def execute(self, context):
        
        global _is_closure
        
        _is_closure = not _is_closure

        return {'FINISHED'}

class toggleOriginOfRelativeFrameNumber(bpy.types.Operator):
    bl_idname = "uiler.toggleoriginofrelativeframenumber"
    bl_label = "label"
    
    origin = bpy.props.BoolProperty()

    def execute(self, context):
        
        scene = context.scene
        propgrp = scene.uil_op_step_reduce_tools_propgrp
        propgrp.uil_relative_frame_number_origin = self.origin
        
        _updateFrame(scene)

        return {'FINISHED'}


#########################################################
# UI
#########################################################
_op = None

def draw(layout, context):

    row = layout.split(0.07, align=True)
    scene = context.scene
    propgrp = scene.uil_op_step_reduce_tools_propgrp

    if _is_closure:
        row.operator("uiler.toggleclosurerelativeframenumberui", text="", icon="DISCLOSURE_TRI_RIGHT")
    else:
        row.operator("uiler.toggleclosurerelativeframenumberui", text="", icon="DISCLOSURE_TRI_DOWN")
    
        row = row.split(0.8, align=True)
        row.prop(propgrp, "uil_relative_frame_number_current_frame", text="Rel")
        
        row = row.split(0.5, align=True)
        origin = propgrp.uil_relative_frame_number_origin
        if origin:
            row.operator("uiler.toggleoriginofrelativeframenumber", text="1").origin = False
        else:
            row.operator("uiler.toggleoriginofrelativeframenumber", text="0").origin = True
        
        if propgrp.uil_relative_frame_number_refresh_auto:
            row.prop(propgrp, "uil_relative_frame_number_refresh_auto", icon="LINKED", toggle=True, text="")
        else:
            row.prop(propgrp, "uil_relative_frame_number_refresh_auto", icon="UNLINKED", toggle=True, text="")

from bpy.app.handlers import persistent

@persistent
def _initForDraw(dummy):
    
    for scene in bpy.data.scenes:
 
        _updateFrame(scene)
    

@persistent
def _updateCurrentFrame(dummy):
    
    scene = bpy.context.scene 
    propgrp = scene.uil_op_step_reduce_tools_propgrp
    if common.isActiveAddonFunctionByName(_FUNCTION_NAME) and propgrp.uil_relative_frame_number_refresh_auto:
        _updateFrame(scene)

def _updateFrame(scene):
    
    propgrp = scene.uil_op_step_reduce_tools_propgrp
    origin_offset = 0
    if not propgrp.uil_relative_frame_number_origin:
        origin_offset = -1
    
    if scene.frame_start > 0:
        propgrp.uil_relative_frame_number_current_frame = scene.frame_current - scene.frame_start + 1 + origin_offset
    else:
        offset = 1 + abs(scene.frame_start)
        propgrp.uil_relative_frame_number_current_frame = scene.frame_current - scene.frame_start + offset + origin_offset

@persistent
def _disableUpdateCurrentFrame(dummy):
    
    global _is_render
    _is_render = True        

@persistent
def _enableUpdateCurrentFrame(dummy):

    global _is_render
    _is_render = False        

bpy.app.handlers.load_post.append(_initForDraw)
bpy.app.handlers.frame_change_post.append(_updateCurrentFrame)
bpy.app.handlers.render_init.append(_disableUpdateCurrentFrame)
bpy.app.handlers.render_cancel.append(_enableUpdateCurrentFrame)
bpy.app.handlers.render_complete.append(_enableUpdateCurrentFrame)


