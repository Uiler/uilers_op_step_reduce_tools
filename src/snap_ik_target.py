import bpy
import re
from collections import OrderedDict
import time

from asyncore import poll
from . import snap_cursor_button
from . import common

#########################################################
# Constants
#########################################################
_RANGE_TYPE_CURRENT = "CURRENT"
_RANGE_TYPE_ALL = "ALL FRAMES"
_RANGE_TYPE_RANGE = "RANGE"
_WAIT_COUNT = 5

#########################################################
# Global Variables
#########################################################
_is_closure = False
_is_range = False

#########################################################
# Functions(Private)
#########################################################
def updateRangeType(self, context):
    
    setRangeNumberVisible()

def setRangeNumberVisible():
    
    global _is_range
    
    propgrp = bpy.context.scene.uil_op_step_reduce_tools_propgrp
    rType = propgrp.uil_snap_ik_range_type
    
    if rType == _RANGE_TYPE_ALL:
        _is_range = False
    elif rType == _RANGE_TYPE_RANGE:
        _is_range = True
    elif rType == _RANGE_TYPE_CURRENT:
        _is_range = False
    else:
        _is_range = True

#########################################################
# Actions
#########################################################
# ret key:ik target bone name(String) / value: chain root bone name(String)
def _getIKBonesMap(context):
    
    ret = {}
    obj = context.active_object
    propgrp = context.scene.uil_op_step_reduce_tools_propgrp
    
    for bone in obj.pose.bones:
        
        if len(bone.constraints) <= 0:
            continue
        
        for con in bone.constraints:
            
            if con.mute and not propgrp.uil_snap_ik_target_enable_mute_const:
                continue
            
            if con.type == "IK":
                
                if not con.subtarget:
                    continue
                
                if con.subtarget not in ret.keys():
                    ret[con.subtarget] = []
                
                ret[con.subtarget].append(bone.name)
        
    
    return ret

class SnapIKTarget2ChainRoot(bpy.types.Operator):
    bl_idname = "uiler.snapiktarget2chainroot"
    bl_label = "Snap IK"
    bl_options = {'REGISTER', 'UNDO'}

    # argument
    isSelected = bpy.props.BoolProperty(default=False)
 
    def execute(self, context):

        propgrp = context.scene.uil_op_step_reduce_tools_propgrp
 
        vshade_now = context.space_data.viewport_shade
        frame_curr = context.scene.frame_current
        obj = context.active_object
        act = obj.animation_data.action
        bones = obj.pose.bones
        activeBone = context.active_pose_bone
        visibleMap = common.getVisibleMapOfPoseBone(bones)
        offset = propgrp.uil_snap_ik_target_offset
        t_start = propgrp.uil_snap_ik_target_start
        t_end = propgrp.uil_snap_ik_target_end
        rType = propgrp.uil_snap_ik_range_type
        map = _getIKBonesMap(context)
        kfrmMin = 2**31-1
        kfrmMax = -2**31
         
        # genarate execution map
        execBoneMap = {}
        for key in map.keys():
             
            bone_tgt = bones[key]
            if self.isSelected and not bone_tgt.bone.select:
                continue
            
            if not common.isVisibleBone(bone_tgt.bone):
                continue
            
            bone_root = None
            roots = map[key]
            maxIdx = len(roots) - 1
            if offset > maxIdx:
                bone_root = bones[roots[maxIdx]]
            else:
                bone_root = bones[roots[offset]]
 
            execBoneMap[bone_tgt] = bone_root
 
         
        for bone_tgt in execBoneMap.keys():
            _snapIKTarget2Root(context, bone_tgt, execBoneMap[bone_tgt])

        # finish
        common.revertBoneVisibleByMap(bones, visibleMap)
        if activeBone:
            obj.data.bones.active = activeBone.bone
 
        return {'FINISHED'}

class SnapIKTarget2ChainRootFrames(bpy.types.Operator):
    bl_idname = "uiler.snapiktarget2chainrootframes"
    bl_label = "Snap IK"
    bl_options = {'REGISTER', 'UNDO'}

    # argument
    isSelected = bpy.props.BoolProperty(default=False)

    _timer = None
    start = bpy.props.IntProperty(default=2**31-1)
    end = bpy.props.IntProperty(default=-2**31)
    _execKfrmMap = OrderedDict()
    _vshade_now = {}
    _frame_current = 0
    _target_now = None
    _visibleMap = {}
    _bones = None
    _activeBone = None
    _count = -1

    def __init__(self):
        pass

    def _finish(self, context):

        for area in bpy.context.screen.areas:
            
            if area.type == "VIEW_3D":
                area.spaces[0].viewport_shade = self._vshade_now[area.spaces[0]]

        context.scene.frame_current = self._frame_current
        common.revertBoneVisibleByMap(self._bones, self._visibleMap)
        if self._activeBone:
            context.active_object.data.bones.active = self._activeBone.bone
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    def modal(self, context, event):
        if event.type == 'TIMER':
            if 0 <= self._count and self._count <= _WAIT_COUNT:
                self._count += 1
                return {'RUNNING_MODAL'}

            if self._target_now:
                
                for bonetuple in self._target_now:
                    _snapIKTarget2Root(context, bonetuple[0], bonetuple[1])
                
                self._target_now = None
                self._count = -1
                
                return {'RUNNING_MODAL'}
            
            else:
            
                try:
                    execKfrm = self._execKfrmMap.popitem(last=False)
                    frm = execKfrm[0]
    
                    if not (self.start <= frm <= self.end):
                        return {'RUNNING_MODAL'}
             
                    context.scene.frame_current = frm
                    self._target_now = execKfrm[1]
                    self._count = 0
                
                except:
                    self._finish(context)
                    return {'FINISHED'}
            
            return {'RUNNING_MODAL'}
        
        elif event.type in {'ESC'}:  # Cancel
            self._finish(context)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
 
        for area in bpy.context.screen.areas:
            
            if area.type == "VIEW_3D":
                self._vshade_now[area.spaces[0]] = area.spaces[0].viewport_shade
                area.spaces[0].viewport_shade = "BOUNDBOX"

        propgrp = context.scene.uil_op_step_reduce_tools_propgrp
        
        self._frame_current = context.scene.frame_current
        obj = context.active_object
        act = obj.animation_data.action
        self._bones = bones = obj.pose.bones
        self._activeBone = context.active_pose_bone
        self._visibleMap = common.getVisibleMapOfPoseBone(bones)
        offset = propgrp.uil_snap_ik_target_offset
        t_start = propgrp.uil_snap_ik_target_start
        t_end = propgrp.uil_snap_ik_target_end
        rType = propgrp.uil_snap_ik_range_type
        map = _getIKBonesMap(context)
        kfrmMin = 2**31-1
        kfrmMax = -2**31
         
        # genarate execution map
        self._execKfrmMap = OrderedDict()
        for key in map.keys():
             
            bone_tgt = bones[key]
            if self.isSelected and not bone_tgt.bone.select:
                continue
             
            if not common.isVisibleBone(bone_tgt.bone):
                continue
            
            bone_root = None
            roots = map[key]
            maxIdx = len(roots) - 1
            if offset > maxIdx:
                bone_root = bones[roots[maxIdx]]
            else:
                bone_root = bones[roots[offset]]
 
            kfrmsAll = _getKeyframeSet(act, bone_tgt)
            for key in kfrmsAll:
                if key not in self._execKfrmMap:
                    self._execKfrmMap[key] = []
                 
                self._execKfrmMap[key].append((bone_tgt, bone_root))
                 
                if kfrmMax < key:
                    kfrmMax = key
                 
                if key < kfrmMin:
                    kfrmMin = key
         

        self.start = kfrmMin
        self.end = kfrmMax
        if rType == _RANGE_TYPE_RANGE:
            self.start = t_start
            self.end = t_end

        # timer start
        wm = context.window_manager
        self._timer = wm.event_timer_add(time_step=0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}


def _snapIKTarget2Root(context, bone_tgt, bone_root):
    
    snapVec = bone_root.tail.copy()
    bpy.ops.pose.select_all(action='DESELECT')

    bone_tgt.bone.select = True
    cursorNow = snap_cursor_button._getCursorLocation(context).copy()
    snap_cursor_button._setCursorLocation(context, snapVec)
    bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
    snap_cursor_button._setCursorLocation(context, cursorNow)
    

# only use dict keys()
def _getKeyframeSet(act, bone_tgt):
    
    kfrmsAll = OrderedDict()
    # Location f-curve search
    for idx in range(3):
        fc = act.fcurves.find('pose.bones["' +  bone_tgt.name + '"].location', idx)
        if not fc:
            continue
        
        kfrms = fc.keyframe_points
        if not kfrms:
            continue
        
        for  kfrm in kfrms:
            kfrmsAll[kfrm.co.x] = None

    # Rotation(Quatanion) f-curve match
    for idx in range(4):
        fc = act.fcurves.find('pose.bones["' +  bone_tgt.name + '"].rotation_quaternion', idx)
        if not fc:
            continue
        
        kfrms = fc.keyframe_points
        if not kfrms:
            continue
        
        for  kfrm in kfrms:
            kfrmsAll[kfrm.co.x] = None
    
    # Rotation(Euler) f-curve_match
    for idx in range(3):
        fc = act.fcurves.find('pose.bones["' +  bone_tgt.name + '"].rotation_euler', idx)
        if not fc:
            continue
        
        kfrms = fc.keyframe_points
        if not kfrms:
            continue
        
        for  kfrm in kfrms:
            kfrmsAll[kfrm.co.x] = None

    # Scale f-curve match
    for idx in range(3):
        fc = act.fcurves.find('pose.bones["' +  bone_tgt.name + '"].scale', idx)
        if not fc:
            continue
        
        kfrms = fc.keyframe_points
        if not kfrms:
            continue
        
        for  kfrm in kfrms:
            kfrmsAll[kfrm.co.x] = None
            
    return kfrmsAll

#####################
#  Closure
class toggleClosureSnapIKTarget(bpy.types.Operator):
    bl_idname = "uiler.toggleclosuresnapiktarget"
    bl_label = "label"

    def execute(self, context):
        
        global _is_closure
        
        _is_closure = not _is_closure

        return {'FINISHED'}

class PickIKSnapRangeStartFromCurrent(bpy.types.Operator):
    bl_idname = "uiler.pickiksnaprangestartfromcurrent"
    bl_label = "label"

    def execute(self, context):
        
        propgrp = context.scene.uil_op_step_reduce_tools_propgrp
        propgrp.uil_snap_ik_target_start = context.scene.frame_current

        return {'FINISHED'}

class PickIKSnapRangeEndFromCurrent(bpy.types.Operator):
    bl_idname = "uiler.pickiksnaprangeendfromcurrent"
    bl_label = "label"

    def execute(self, context):
        
        propgrp = context.scene.uil_op_step_reduce_tools_propgrp
        propgrp.uil_snap_ik_target_end = context.scene.frame_current

        return {'FINISHED'}

class PickIKSnapRangeStartAndEndFromSceneStartAndEnd(bpy.types.Operator):
    bl_idname = "uiler.pickiksnaprangestartandendfromscenestartandend"
    bl_label = "label"

    def execute(self, context):
        
        propgrp = context.scene.uil_op_step_reduce_tools_propgrp
        propgrp.uil_snap_ik_target_start = context.scene.frame_start
        propgrp.uil_snap_ik_target_end = context.scene.frame_end

        return {'FINISHED'}

#########################################################
# UI
#########################################################
def draw(layout, context):

    propgrp = context.scene.uil_op_step_reduce_tools_propgrp

    split = layout.split(0.1)
    row = split.row()
    isPosframes = propgrp.uil_snap_ik_range_type != _RANGE_TYPE_CURRENT and not context.scene.tool_settings.use_keyframe_insert_auto
    
    if _is_closure:
        row.operator("uiler.toggleclosuresnapiktarget", text="", icon="DISCLOSURE_TRI_RIGHT")
    else:
        row.operator("uiler.toggleclosuresnapiktarget", text="", icon="DISCLOSURE_TRI_DOWN")

        row = split.row(align=True)
        split2 = row.split(0.85, align=True)
        row = split2.row(align=True)
        if context.mode != "POSE":
            row.enabled = False
        if isPosframes:
            row.enabled = False
        split3 = row.split(0.35, align=True)
        row = split3.row(align=True)
        row.label(text="Snap ", icon="SNAP_ON")
        row = split3.row(align=True)
        if propgrp.uil_snap_ik_range_type == _RANGE_TYPE_CURRENT:
            row.operator("uiler.snapiktarget2chainroot", text="Selected").isSelected = True
            row.operator("uiler.snapiktarget2chainroot", text="All IK TGT").isSelected = False
        else:
            row.operator("uiler.snapiktarget2chainrootframes", text="Selected").isSelected = True
            row.operator("uiler.snapiktarget2chainrootframes", text="All IK TGT").isSelected = False
        row = split2.row(align=True)
        row.prop(propgrp, "uil_snap_ik_target_enable_mute_const", toggle=True, text="mute")
        
        row = layout.row(align=True)
        row.prop(propgrp, "uil_snap_ik_range_type", expand=True)

        if isPosframes:
            row = layout.row(align=True)
            row.prop(context.scene.tool_settings, "use_keyframe_insert_auto", text="", toggle=True)
            row.prop_search(context.scene.keying_sets_all, "active", context.scene, "keying_sets_all", text="")
            row = layout.row()
            row.alignment = "RIGHT"
            row.label(icon = 'ERROR', text='Activate auto keyframe insertion.')
        
        if propgrp.uil_snap_ik_range_type != _RANGE_TYPE_CURRENT:
            
            row = layout.row(align=True)
            col = row.split(0.3)
            row = col.row(align=True)
            row.prop(propgrp, "uil_snap_ik_target_offset", text="Offset")
            row = col.row(align=True)
            if not _is_range:
                row.enabled = False
            row.operator("uiler.pickiksnaprangestartfromcurrent", text="", icon="TIME")
            row.prop(propgrp, "uil_snap_ik_target_start", text="Start")
            row.prop(propgrp, "uil_snap_ik_target_end", text="End")
            row.operator("uiler.pickiksnaprangeendfromcurrent", text="", icon="TIME")
            row.operator("uiler.pickiksnaprangestartandendfromscenestartandend", text="", icon="FILE_REFRESH")

from bpy.app.handlers import persistent

@persistent
def _initForDraw(dummy):

    setRangeNumberVisible()

bpy.app.handlers.load_post.append(_initForDraw)        


