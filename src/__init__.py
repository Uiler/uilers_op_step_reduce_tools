import bpy
import re

from asyncore import poll

from . import insert_all_channel_keyframes
from . import keyframe_type_button
from . import keyframe_type_button_on_dopesheet
from . import move_current_frame
from . import pivot_point_button
from . import snap_cursor_button
from . import global_bone_selection_set
from .global_bone_selection_set import BoneSelectionSetPropGrp
from . import sort_dopesheet_channels
from . import keying_tools
from . import snap_ik_target
from . import viewport_shade_button
from . import jump_to_timeline_markers
from . import relative_frame_number
from . import transform_orientation_button

bl_info = {
    "name" : "Uiler's Operation step reduce tools",
    "author" : "Uiler",
    "version" : (0,1), 
    "blender" : (2, 7, 8),
    "location" : "User",
    "description" : "Reduce operation number of steps.",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
    "category" : "User"
}

#########################################################
# Constants
#########################################################
_FUNCTION_ENUM_INSERT_ALL_CHANNEL_KEYFRAMES = "INSERT_ALL_CHANNEL_KEYFRAMES"
_FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON = "KEYFRAME_TYPE_BUTTON"
_FUNCTION_ENUM_MOVE_CURRENT_FRAME = "MOVE_CURRENT_FRAME"
_FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET = "KEYFRAME_TYPE_BUTTON_ON_DOPESHEET"
_FUNCTION_ENUM_PIVOT_POINT_BUTTON = "PIVOT_POINT_BUTTON"
_FUNCTION_ENUM_SNAP_CURSOR_BUTTON = "SNAP_CURSOR_BUTTON"
_FUNCTION_ENUM_GLOBAL_BONE_SELECTION_SET = "GLOBAL_BONE_SELECTION_SET"
_FUNCTION_ENUM_SORT_CHANNELS_ON_DOPESHEET = "SORT_CHANNELS_ON_DOPESHEET"
_FUNCTION_ENUM_KEYING_TOOLS = "KEYING_TOOLS"
_FUNCTION_ENUM_SNAP_IK_TARGET = "SNAP_IK_TARGET"
_FUNCTION_ENUM_VIEWPORT_SHADE_BUTTON = "VIEWPORT_SHADE_BUTTON"
_FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS = "JUMP_TO_TIMELINE_MARKERS"
_FUNCTION_ENUM_RELATIVE_FRAME_NUMBER = "RELATIVE_FRAME_NUMBER"
_FUNCTION_ENUM_TRANSFORM_ORIENTATION_BUTTON = "TRANSFORM_ORIENTATION_BUTTON"

_FUNCTION_ENUM_INSERT_ALL_CHANNEL_KEYFRAMES_DSC = "Insert all channel keyframes"
_FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_DSC = "Keyframe type button(3D View)"
_FUNCTION_ENUM_MOVE_CURRENT_FRAME_DSC = "Move Current Frame Increment"
_FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET_DSC = "Keyframe type button(Dopesheet)"
_FUNCTION_ENUM_PIVOT_POINT_BUTTON_DSC = "Pivot point button"
_FUNCTION_ENUM_SNAP_CURSOR_BUTTON_DSC = "Snap cursor button"
_FUNCTION_ENUM_GLOBAL_BONE_SELECTION_SET_DSC = "Global version of Bone selection set"
_FUNCTION_ENUM_SORT_CHANNELS_ON_DOPESHEET_DSC = "Sort channels on dopesheet"
_FUNCTION_ENUM_KEYING_TOOLS_DSC = "Put Keying tools to another place"
_FUNCTION_ENUM_SNAP_IK_TARGET_DSC = "Snap IK Target to chain root"
_FUNCTION_ENUM_VIEWPORT_SHADE_BUTTON_DSC = "Viewport shade button"
_FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS_DSC = "Jump to next/prev/name timeline marker"
_FUNCTION_ENUM_RELATIVE_FRAME_NUMBER_DSC = "Relative frame number from start frame"
_FUNCTION_ENUM_TRANSFORM_ORIENTATION_BUTTON_DSC = "Transform orientation button"

_FUNCTION_ENUM = {
    _FUNCTION_ENUM_INSERT_ALL_CHANNEL_KEYFRAMES : _FUNCTION_ENUM_INSERT_ALL_CHANNEL_KEYFRAMES_DSC,
    _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON : _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_DSC,
    _FUNCTION_ENUM_MOVE_CURRENT_FRAME : _FUNCTION_ENUM_MOVE_CURRENT_FRAME_DSC,
    _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET : _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET_DSC,
    _FUNCTION_ENUM_PIVOT_POINT_BUTTON : _FUNCTION_ENUM_PIVOT_POINT_BUTTON_DSC,
    _FUNCTION_ENUM_SNAP_CURSOR_BUTTON : _FUNCTION_ENUM_SNAP_CURSOR_BUTTON_DSC,
    _FUNCTION_ENUM_GLOBAL_BONE_SELECTION_SET : _FUNCTION_ENUM_GLOBAL_BONE_SELECTION_SET_DSC,
    _FUNCTION_ENUM_SORT_CHANNELS_ON_DOPESHEET : _FUNCTION_ENUM_SORT_CHANNELS_ON_DOPESHEET_DSC,
    _FUNCTION_ENUM_KEYING_TOOLS : _FUNCTION_ENUM_KEYING_TOOLS_DSC,
    _FUNCTION_ENUM_SNAP_IK_TARGET : _FUNCTION_ENUM_SNAP_IK_TARGET_DSC,
    _FUNCTION_ENUM_VIEWPORT_SHADE_BUTTON : _FUNCTION_ENUM_VIEWPORT_SHADE_BUTTON_DSC,
    _FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS : _FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS_DSC,
    _FUNCTION_ENUM_RELATIVE_FRAME_NUMBER : _FUNCTION_ENUM_RELATIVE_FRAME_NUMBER_DSC,
    _FUNCTION_ENUM_TRANSFORM_ORIENTATION_BUTTON : _FUNCTION_ENUM_TRANSFORM_ORIENTATION_BUTTON_DSC
}

_FUNCTION_EXEC_ENUM = {
    _FUNCTION_ENUM_INSERT_ALL_CHANNEL_KEYFRAMES : insert_all_channel_keyframes.draw,
    _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON : keyframe_type_button.draw,
    _FUNCTION_ENUM_MOVE_CURRENT_FRAME : move_current_frame.draw,
    _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET : keyframe_type_button_on_dopesheet.draw,
    _FUNCTION_ENUM_PIVOT_POINT_BUTTON : pivot_point_button.draw,
    _FUNCTION_ENUM_SNAP_CURSOR_BUTTON : snap_cursor_button.draw,
    _FUNCTION_ENUM_GLOBAL_BONE_SELECTION_SET : global_bone_selection_set.draw,
    _FUNCTION_ENUM_SORT_CHANNELS_ON_DOPESHEET : sort_dopesheet_channels.draw,
    _FUNCTION_ENUM_KEYING_TOOLS : keying_tools.draw,
    _FUNCTION_ENUM_SNAP_IK_TARGET : snap_ik_target.draw,
    _FUNCTION_ENUM_VIEWPORT_SHADE_BUTTON : viewport_shade_button.draw,
    _FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS : jump_to_timeline_markers.draw,
    _FUNCTION_ENUM_RELATIVE_FRAME_NUMBER : relative_frame_number.draw,
    _FUNCTION_ENUM_TRANSFORM_ORIENTATION_BUTTON : transform_orientation_button.draw
}


_ADD_TARGET_VIEW_3D_HEADER = "fns_3dview_header"
_ADD_TARGET_VIEW_3D_UI = "fns_3dview_ui"
_ADD_TARGET_VIEW_3D_TOOLS = "fns_3dview_tools"
_ADD_TARGET_TIMELINE_HEADER = "fns_timeline_header"
_ADD_TARGET_DOPESHEET_HEADER = "fns_dopesheet_header"
_ADD_TARGET_DOPESHEET_UI = "fns_dopesheet_ui"

#########################################################
# Global Variables
#########################################################

#########################################################
# Properties
#########################################################
class OPStepReduceToolsSceneProperties(bpy.types.PropertyGroup):
    
    # :see relative_frame_number.py
    uil_relative_frame_number_current_frame = bpy.props.IntProperty(name="uil_relative_frame_number_current_frame", description="Relative frame from start frame.", default=0, step=1, subtype='NONE', update=relative_frame_number.updateRelative)
    uil_relative_frame_number_refresh_auto = bpy.props.BoolProperty(name="uil_relative_frame_number_refresh_auto", description="Refresh automatically when frame current be updated.", default=True, subtype='NONE')
    uil_relative_frame_number_origin = bpy.props.BoolProperty(name="uil_relative_frame_number_origin", description="Origin of relative frame number.0-origin or 1-origin.", default=True, subtype="NONE")

    # :see snap_ik_target.py
    uil_snap_ik_target_offset = bpy.props.IntProperty(name="uil_snap_ik_target_offset", description="Offset number if bone is target from multiple bones.", default=0, min=0, soft_min=0, step=1, subtype='NONE')
    uil_snap_ik_target_start = bpy.props.IntProperty(name="uil_snap_ik_target_start", description="Starting frame of range of snap ik target to chain root.", default=0, step=1, subtype='NONE')
    uil_snap_ik_target_end = bpy.props.IntProperty(name="uil_snap_ik_target_end", description="End frame of range of snap ik target to chain root.", default=250, step=1, subtype='NONE')
    uil_snap_ik_target_enable_mute_const = bpy.props.BoolProperty(name="uil_snap_ik_target_enable_mute_const", description="Get muted ik constraints.", default=False)

    _RANGE_TYPE_CURRENT = snap_ik_target._RANGE_TYPE_CURRENT
    _RANGE_TYPE_ALL = snap_ik_target._RANGE_TYPE_ALL
    _RANGE_TYPE_RANGE = snap_ik_target._RANGE_TYPE_RANGE

    it = []
    it.append((_RANGE_TYPE_CURRENT, _RANGE_TYPE_CURRENT, "Execute snap on current frame.","", 0))
    it.append((_RANGE_TYPE_RANGE, _RANGE_TYPE_RANGE, "Execute snap on keyframe points between range.","", 1))
    it.append((_RANGE_TYPE_ALL, _RANGE_TYPE_ALL, "Execute snap on keyframe points between min to max.","", 2))
    uil_snap_ik_range_type = bpy.props.EnumProperty(items = it, default=_RANGE_TYPE_CURRENT, update=snap_ik_target.updateRangeType)
    

def _defProperties():

    # Define Addon's Properties
    bpy.types.Scene.uil_op_step_reduce_tools_propgrp = bpy.props.PointerProperty(type=OPStepReduceToolsSceneProperties)




#########################################################
# Functions(Private)
#########################################################
#########################################################
# Actions
#########################################################
class AddFunction(bpy.types.Operator):
    bl_idname = "uiler.addopstepreducetoolsfunctiontoui"
    bl_label = "Add UI"
    bl_options = {'REGISTER', 'UNDO'}
    
    target = bpy.props.StringProperty()

    def execute(self, context):

        user_preferences = context.user_preferences
        prefs = user_preferences.addons[__package__].preferences
 
        item = eval("prefs." + self.target + ".add()")
        item.id = len(eval("prefs." + self.target))
        item.name = _FUNCTION_ENUM[eval("prefs." + self.target + "_enum")]
        item.value = eval("prefs." + self.target + "_enum")
        exec("prefs." + self.target +"_idx = (len(prefs. " + self.target + ")-1)")
        

        return {'FINISHED'}

class RemoveFunction(bpy.types.Operator):
    bl_idname = "uiler.removeopstepreducetoolsfunctiontoui"
    bl_label = "Remove UI"
    bl_options = {'REGISTER', 'UNDO'}
    
    target = bpy.props.StringProperty()

    def execute(self, context):

        user_preferences = context.user_preferences
        prefs = user_preferences.addons[__package__].preferences
 
        idx = eval("prefs." + self.target + "_idx")
        eval("prefs." + self.target + ".remove(idx)")

        return {'FINISHED'}

class UpFunction(bpy.types.Operator):
    bl_idname = "uiler.upopstepreducetoolsfunctiontoui"
    bl_label = "Up order"
    bl_options = {'REGISTER', 'UNDO'}
    
    target = bpy.props.StringProperty()

    def execute(self, context):

        user_preferences = context.user_preferences
        prefs = user_preferences.addons[__package__].preferences
 
        idx = eval("prefs." + self.target + "_idx")
        
        if idx < 1:
            return {'FINISHED'}
            
        length = eval("len(prefs." + self.target + ")")
        eval("prefs." + self.target + ".move(idx, idx-1)")
        exec("prefs." + self.target + "_idx -= 1")

        return {'FINISHED'}

class DownFunction(bpy.types.Operator):
    bl_idname = "uiler.downopstepreducetoolsfunctiontoui"
    bl_label = "Down order"
    bl_options = {'REGISTER', 'UNDO'}
    
    target = bpy.props.StringProperty()

    def execute(self, context):

        user_preferences = context.user_preferences
        prefs = user_preferences.addons[__package__].preferences
 
        idx = eval("prefs." + self.target + "_idx")
        length = eval("len(prefs." + self.target + ")")
        
        if idx > length-2:
            return {'FINISHED'}
            
        eval("prefs." + self.target + ".move(idx, idx+1)")
        exec("prefs." + self.target + "_idx += 1")

        return {'FINISHED'}

#########################################################
# UI
#########################################################
class FunctionList_items(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False, translate=False, icon="BOOKMARKS")

    def invoke(self, context, event):
        pass   

class FunctionPropGrp(bpy.types.PropertyGroup):
    '''name = bpy.props.StringProperty() '''
    id = bpy.props.IntProperty()
    value = bpy.props.StringProperty()

class OpStepReduceToolsAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    _function_type = []
    _function_type.append((_FUNCTION_ENUM_INSERT_ALL_CHANNEL_KEYFRAMES, _FUNCTION_ENUM_INSERT_ALL_CHANNEL_KEYFRAMES_DSC,  _FUNCTION_ENUM_INSERT_ALL_CHANNEL_KEYFRAMES_DSC))
    _function_type.append((_FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON, _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_DSC,  _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_DSC))
    _function_type.append((_FUNCTION_ENUM_MOVE_CURRENT_FRAME, _FUNCTION_ENUM_MOVE_CURRENT_FRAME_DSC,  _FUNCTION_ENUM_MOVE_CURRENT_FRAME_DSC))
    _function_type.append((_FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET, _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET_DSC,  _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET_DSC))
    _function_type.append((_FUNCTION_ENUM_PIVOT_POINT_BUTTON, _FUNCTION_ENUM_PIVOT_POINT_BUTTON_DSC,  _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET_DSC))
    _function_type.append((_FUNCTION_ENUM_SNAP_CURSOR_BUTTON, _FUNCTION_ENUM_SNAP_CURSOR_BUTTON_DSC,  _FUNCTION_ENUM_SNAP_CURSOR_BUTTON_DSC))
    _function_type.append((_FUNCTION_ENUM_GLOBAL_BONE_SELECTION_SET, _FUNCTION_ENUM_GLOBAL_BONE_SELECTION_SET_DSC,  _FUNCTION_ENUM_GLOBAL_BONE_SELECTION_SET_DSC))
    _function_type.append((_FUNCTION_ENUM_KEYING_TOOLS, _FUNCTION_ENUM_KEYING_TOOLS_DSC,  _FUNCTION_ENUM_KEYING_TOOLS_DSC))
    _function_type.append((_FUNCTION_ENUM_SNAP_IK_TARGET, _FUNCTION_ENUM_SNAP_IK_TARGET_DSC,  _FUNCTION_ENUM_SNAP_IK_TARGET_DSC))
    _function_type.append((_FUNCTION_ENUM_VIEWPORT_SHADE_BUTTON, _FUNCTION_ENUM_VIEWPORT_SHADE_BUTTON_DSC, _FUNCTION_ENUM_VIEWPORT_SHADE_BUTTON_DSC))
    _function_type.append((_FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS, _FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS_DSC, _FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS_DSC))
    _function_type.append((_FUNCTION_ENUM_RELATIVE_FRAME_NUMBER, _FUNCTION_ENUM_RELATIVE_FRAME_NUMBER_DSC, _FUNCTION_ENUM_RELATIVE_FRAME_NUMBER_DSC))
    _function_type.append((_FUNCTION_ENUM_TRANSFORM_ORIENTATION_BUTTON, _FUNCTION_ENUM_TRANSFORM_ORIENTATION_BUTTON_DSC, _FUNCTION_ENUM_TRANSFORM_ORIENTATION_BUTTON_DSC))

    _function_type_3dview = []
    _function_type_3dview.append((_FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON, _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_DSC,  _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_DSC))
    _function_type_3dview.append((_FUNCTION_ENUM_MOVE_CURRENT_FRAME, _FUNCTION_ENUM_MOVE_CURRENT_FRAME_DSC,  _FUNCTION_ENUM_MOVE_CURRENT_FRAME_DSC))
    _function_type_3dview.append((_FUNCTION_ENUM_PIVOT_POINT_BUTTON, _FUNCTION_ENUM_PIVOT_POINT_BUTTON_DSC,  _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET_DSC))
    _function_type_3dview.append((_FUNCTION_ENUM_SNAP_CURSOR_BUTTON, _FUNCTION_ENUM_SNAP_CURSOR_BUTTON_DSC,  _FUNCTION_ENUM_SNAP_CURSOR_BUTTON_DSC))
    _function_type_3dview.append((_FUNCTION_ENUM_GLOBAL_BONE_SELECTION_SET, _FUNCTION_ENUM_GLOBAL_BONE_SELECTION_SET_DSC,  _FUNCTION_ENUM_GLOBAL_BONE_SELECTION_SET_DSC))
    _function_type_3dview.append((_FUNCTION_ENUM_KEYING_TOOLS, _FUNCTION_ENUM_KEYING_TOOLS_DSC,  _FUNCTION_ENUM_KEYING_TOOLS_DSC))
    _function_type_3dview.append((_FUNCTION_ENUM_SNAP_IK_TARGET, _FUNCTION_ENUM_SNAP_IK_TARGET_DSC,  _FUNCTION_ENUM_SNAP_IK_TARGET_DSC))
    _function_type_3dview.append((_FUNCTION_ENUM_VIEWPORT_SHADE_BUTTON, _FUNCTION_ENUM_VIEWPORT_SHADE_BUTTON_DSC, _FUNCTION_ENUM_VIEWPORT_SHADE_BUTTON_DSC))
    _function_type_3dview.append((_FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS, _FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS_DSC, _FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS_DSC))
    _function_type_3dview.append((_FUNCTION_ENUM_RELATIVE_FRAME_NUMBER, _FUNCTION_ENUM_RELATIVE_FRAME_NUMBER_DSC, _FUNCTION_ENUM_RELATIVE_FRAME_NUMBER_DSC))
    _function_type_3dview.append((_FUNCTION_ENUM_TRANSFORM_ORIENTATION_BUTTON, _FUNCTION_ENUM_TRANSFORM_ORIENTATION_BUTTON_DSC, _FUNCTION_ENUM_TRANSFORM_ORIENTATION_BUTTON_DSC))

    _function_type_3dview_header = []
    _function_type_3dview_header.append((_FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON, _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_DSC,  _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_DSC))
    _function_type_3dview_header.append((_FUNCTION_ENUM_MOVE_CURRENT_FRAME, _FUNCTION_ENUM_MOVE_CURRENT_FRAME_DSC,  _FUNCTION_ENUM_MOVE_CURRENT_FRAME_DSC))
    _function_type_3dview_header.append((_FUNCTION_ENUM_PIVOT_POINT_BUTTON, _FUNCTION_ENUM_PIVOT_POINT_BUTTON_DSC,  _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET_DSC))
    _function_type_3dview_header.append((_FUNCTION_ENUM_SNAP_CURSOR_BUTTON, _FUNCTION_ENUM_SNAP_CURSOR_BUTTON_DSC,  _FUNCTION_ENUM_SNAP_CURSOR_BUTTON_DSC))
    _function_type_3dview_header.append((_FUNCTION_ENUM_KEYING_TOOLS, _FUNCTION_ENUM_KEYING_TOOLS_DSC,  _FUNCTION_ENUM_KEYING_TOOLS_DSC))
    _function_type_3dview_header.append((_FUNCTION_ENUM_VIEWPORT_SHADE_BUTTON, _FUNCTION_ENUM_VIEWPORT_SHADE_BUTTON_DSC, _FUNCTION_ENUM_VIEWPORT_SHADE_BUTTON_DSC))
    _function_type_3dview_header.append((_FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS, _FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS_DSC, _FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS_DSC))
    _function_type_3dview_header.append((_FUNCTION_ENUM_RELATIVE_FRAME_NUMBER, _FUNCTION_ENUM_RELATIVE_FRAME_NUMBER_DSC, _FUNCTION_ENUM_RELATIVE_FRAME_NUMBER_DSC))
    _function_type_3dview_header.append((_FUNCTION_ENUM_TRANSFORM_ORIENTATION_BUTTON, _FUNCTION_ENUM_TRANSFORM_ORIENTATION_BUTTON_DSC, _FUNCTION_ENUM_TRANSFORM_ORIENTATION_BUTTON_DSC))

    _function_type_dopesheet = []
    _function_type_dopesheet.append((_FUNCTION_ENUM_INSERT_ALL_CHANNEL_KEYFRAMES, _FUNCTION_ENUM_INSERT_ALL_CHANNEL_KEYFRAMES_DSC,  _FUNCTION_ENUM_INSERT_ALL_CHANNEL_KEYFRAMES_DSC))
    _function_type_dopesheet.append((_FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON, _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_DSC,  _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_DSC))
    _function_type_dopesheet.append((_FUNCTION_ENUM_MOVE_CURRENT_FRAME, _FUNCTION_ENUM_MOVE_CURRENT_FRAME_DSC,  _FUNCTION_ENUM_MOVE_CURRENT_FRAME_DSC))
    _function_type_dopesheet.append((_FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET, _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET_DSC,  _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET_DSC))
    _function_type_dopesheet.append((_FUNCTION_ENUM_PIVOT_POINT_BUTTON, _FUNCTION_ENUM_PIVOT_POINT_BUTTON_DSC,  _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET_DSC))
    _function_type_dopesheet.append((_FUNCTION_ENUM_SORT_CHANNELS_ON_DOPESHEET, _FUNCTION_ENUM_SORT_CHANNELS_ON_DOPESHEET_DSC, _FUNCTION_ENUM_SORT_CHANNELS_ON_DOPESHEET_DSC))
    _function_type_dopesheet.append((_FUNCTION_ENUM_KEYING_TOOLS, _FUNCTION_ENUM_KEYING_TOOLS_DSC,  _FUNCTION_ENUM_KEYING_TOOLS_DSC))
    _function_type_dopesheet.append((_FUNCTION_ENUM_SNAP_IK_TARGET, _FUNCTION_ENUM_SNAP_IK_TARGET_DSC,  _FUNCTION_ENUM_SNAP_IK_TARGET_DSC))
    _function_type_dopesheet.append((_FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS, _FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS_DSC, _FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS_DSC))
    _function_type_dopesheet.append((_FUNCTION_ENUM_RELATIVE_FRAME_NUMBER, _FUNCTION_ENUM_RELATIVE_FRAME_NUMBER_DSC, _FUNCTION_ENUM_RELATIVE_FRAME_NUMBER_DSC))
    
    _function_type_dopesheet_header = []
    _function_type_dopesheet_header.append((_FUNCTION_ENUM_INSERT_ALL_CHANNEL_KEYFRAMES, _FUNCTION_ENUM_INSERT_ALL_CHANNEL_KEYFRAMES_DSC,  _FUNCTION_ENUM_INSERT_ALL_CHANNEL_KEYFRAMES_DSC))
    _function_type_dopesheet_header.append((_FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON, _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_DSC,  _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_DSC))
    _function_type_dopesheet_header.append((_FUNCTION_ENUM_MOVE_CURRENT_FRAME, _FUNCTION_ENUM_MOVE_CURRENT_FRAME_DSC,  _FUNCTION_ENUM_MOVE_CURRENT_FRAME_DSC))
    _function_type_dopesheet_header.append((_FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET, _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET_DSC,  _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET_DSC))
    _function_type_dopesheet_header.append((_FUNCTION_ENUM_PIVOT_POINT_BUTTON, _FUNCTION_ENUM_PIVOT_POINT_BUTTON_DSC,  _FUNCTION_ENUM_KEYFRAME_TYPE_BUTTON_ON_DOPESHEET_DSC))
    _function_type_dopesheet_header.append((_FUNCTION_ENUM_KEYING_TOOLS, _FUNCTION_ENUM_KEYING_TOOLS_DSC,  _FUNCTION_ENUM_KEYING_TOOLS_DSC))
    _function_type_dopesheet_header.append((_FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS, _FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS_DSC, _FUNCTION_ENUM_JUMP_TO_TIMELINE_MARKERS_DSC))
    _function_type_dopesheet_header.append((_FUNCTION_ENUM_RELATIVE_FRAME_NUMBER, _FUNCTION_ENUM_RELATIVE_FRAME_NUMBER_DSC, _FUNCTION_ENUM_RELATIVE_FRAME_NUMBER_DSC))

    fns_3dview_header_enum = bpy.props.EnumProperty(items = _function_type_3dview_header, name="", description="function list.", default=_FUNCTION_ENUM_SNAP_CURSOR_BUTTON)
    fns_3dview_header = bpy.props.CollectionProperty(type=FunctionPropGrp)
    fns_3dview_header_idx = bpy.props.IntProperty()

    fns_3dview_ui_enum = bpy.props.EnumProperty(items = _function_type_3dview, name="", description="function list.", default=_FUNCTION_ENUM_SNAP_CURSOR_BUTTON)
    fns_3dview_ui = bpy.props.CollectionProperty(type=FunctionPropGrp)
    fns_3dview_ui_idx = bpy.props.IntProperty()

    fns_3dview_tools_enum = bpy.props.EnumProperty(items = _function_type_3dview, name="", description="function list.", default=_FUNCTION_ENUM_SNAP_CURSOR_BUTTON)
    fns_3dview_tools = bpy.props.CollectionProperty(type=FunctionPropGrp)
    fns_3dview_tools_idx = bpy.props.IntProperty()

    fns_timeline_header_enum = bpy.props.EnumProperty(items = _function_type_3dview_header, name="", description="function list.", default=_FUNCTION_ENUM_MOVE_CURRENT_FRAME)
    fns_timeline_header = bpy.props.CollectionProperty(type=FunctionPropGrp)
    fns_timeline_header_idx = bpy.props.IntProperty()

    fns_dopesheet_header_enum = bpy.props.EnumProperty(items = _function_type_dopesheet_header, name="", description="function list.", default=_FUNCTION_ENUM_INSERT_ALL_CHANNEL_KEYFRAMES)
    fns_dopesheet_header = bpy.props.CollectionProperty(type=FunctionPropGrp)
    fns_dopesheet_header_idx = bpy.props.IntProperty()

    fns_dopesheet_ui_enum = bpy.props.EnumProperty(items = _function_type_dopesheet, name="", description="function list.", default=_FUNCTION_ENUM_SORT_CHANNELS_ON_DOPESHEET)
    fns_dopesheet_ui = bpy.props.CollectionProperty(type=FunctionPropGrp)
    fns_dopesheet_ui_idx = bpy.props.IntProperty()

    # :be used in global_bone_selection_set.py  
    bone_selection_set_grp = bpy.props.CollectionProperty(type=BoneSelectionSetPropGrp)
    bone_selection_set_grp_idx = bpy.props.IntProperty()
    isLockEditGlobalBoneSelectionSet = bpy.props.BoolProperty(default=False)
    isLayerModeGlobalBoneselectionSet = bpy.props.BoolProperty(default=True)

    # :be used in pivot_point_button.py
    pp_state_enum = []
    pp_state_enum.append(("ACTIVE_ELEMENT", "", "","ROTACTIVE", 0))
    pp_state_enum.append(("MEDIAN_POINT", "", "","ROTATECENTER", 1))
    pp_state_enum.append(("INDIVIDUAL_ORIGINS", "", "","ROTATECOLLECTION", 2))
    pp_state_enum.append(("CURSOR", "", "","CURSOR", 3))
    pp_state_enum.append(("BOUNDING_BOX_CENTER", "", "","ROTATE", 4))
    pivot_point_state = bpy.props.EnumProperty(items = pp_state_enum, update=pivot_point_button.update)

    # :be used in keyframe_type_button.py
    kt_state_enum = []
    kt_state_enum.append(("JITTER", "", "","KEYTYPE_JITTER_VEC", 0))
    kt_state_enum.append(("EXTREME", "", "","KEYTYPE_EXTREME_VEC", 1))
    kt_state_enum.append(("MOVING_HOLD", "", "","KEYTYPE_MOVING_HOLD_VEC", 2))
    kt_state_enum.append(("BREAKDOWN", "", "","KEYTYPE_BREAKDOWN_VEC", 3))
    kt_state_enum.append(("KEYFRAME", "", "","KEYTYPE_KEYFRAME_VEC", 4))
    keyframe_type_state = bpy.props.EnumProperty(items = kt_state_enum, update=keyframe_type_button.update)
    
    def _drawParts(self, context, parts, target):
        
        row = parts.row(align=True)
        row.prop(self, target + "_enum")
        row.operator("uiler.addopstepreducetoolsfunctiontoui", text="", icon='ZOOMIN').target = target 
        
        row = parts.row()
        row.template_list("FunctionList_items", target, self, target, self, target + "_idx", rows=2)        

        col = row.column(align=True)
        col.operator("uiler.removeopstepreducetoolsfunctiontoui", text="", icon="PANEL_CLOSE").target = target
        col.separator()
        col.operator("uiler.upopstepreducetoolsfunctiontoui", icon='TRIA_UP', text="").target = target
        col.operator("uiler.downopstepreducetoolsfunctiontoui", icon='TRIA_DOWN', text="").target = target
    
    def draw(self, context):
        layout = self.layout
        
        # 3D View
        view3d = layout.box()
        view3d.label(text="3D View", icon="TRIA_DOWN")

        # 3D View(header)
        view3d_header = view3d.box()
        view3d_header.label(text="Header", icon="TRIA_DOWN")
        target = _ADD_TARGET_VIEW_3D_HEADER
        
        self._drawParts(context, view3d_header, target)

        # 3D View(UI)
        view3d_ui = view3d.box()
        view3d_ui.label(text="Right Panel", icon="TRIA_DOWN")
        target = _ADD_TARGET_VIEW_3D_UI
        self._drawParts(context, view3d_ui, target)

        # 3D View(Tools)
#         view3d_tools = view3d.box()
#         view3d_tools.label(text="Left Panel", icon="TRIA_DOWN")
#         target = _ADD_TARGET_VIEW_3D_TOOLS
#         self._drawParts(context, view3d_tools, target)

        # Timeline
        timeline = layout.box()
        timeline.label(text="Timeline", icon="TRIA_DOWN")
        timeline_header = timeline.box()
        timeline_header.label(text="Header", icon="TRIA_DOWN")
        target = _ADD_TARGET_TIMELINE_HEADER
        self._drawParts(context, timeline_header, target)
        
        # Dopesheet(Header)
        dopesheet = layout.box()
        dopesheet.label(text="Dopesheet", icon="TRIA_DOWN")
        dopesheet_header = dopesheet.box()
        dopesheet_header.label(text="Header", icon="TRIA_DOWN")
        target = _ADD_TARGET_DOPESHEET_HEADER
        self._drawParts(context, dopesheet_header, target)

        # Dopesheet(UI)
        dopesheet_ui = dopesheet.box()
        dopesheet_ui.label(text="Right Panel", icon="TRIA_DOWN")
        target = _ADD_TARGET_DOPESHEET_UI
        self._drawParts(context, dopesheet_ui, target)


def _drawUis(layout, context, target):
    
    user_preferences = context.user_preferences
    prefs = user_preferences.addons[__package__].preferences

    values = eval("prefs." + target)

    for value in values:
        _FUNCTION_EXEC_ENUM[value.value](layout, context)
        
class DrawOpStepReduceToolsUIAtView3dHeader(bpy.types.Header):
#     bl_label = ""
    bl_idname = "UILER_OP_STEP_REDUCE_TOOLS_UI_AT_VIEW3D_HEADER_PT_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return "OK"
    
    def draw(self, context):
        
        layout = self.layout
        
        _drawUis(layout, context, _ADD_TARGET_VIEW_3D_HEADER)

class DrawOpStepReduceToolsUIAtView3dUI(bpy.types.Panel):
    bl_label = "OP Step Reduce Tools"
    bl_idname = "UILER_OP_STEP_REDUCE_TOOLS_UI_AT_VIEW3D_UI_PT_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return "OK"
    
    def draw(self, context):
        
        layout = self.layout
        
        _drawUis(layout, context, _ADD_TARGET_VIEW_3D_UI)

# class DrawOpStepReduceToolsUIAtView3dTools(bpy.types.Panel):
#     bl_label = "OP Step Reduce Tools"
#     bl_idname = "UILER_OP_STEP_REDUCE_TOOLS_UI_AT_VIEW3D_TOOLS_PT_layout"
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'TOOLS'
#     bl_category = "Step Reduce Tools"
#     bl_context = "objectmode"
# 
#     @classmethod
#     def poll(cls, context):
#         return "OK"
#     
#     def draw(self, context):
#         
#         layout = self.layout
#         
#         _drawUis(layout, context, _ADD_TARGET_VIEW_3D_TOOLS)


class DrawOpStepReduceToolsUIAtTimelineHeader(bpy.types.Header):
    bl_label = "OP Step Reduce Tools"
    bl_idname = "UILER_OP_STEP_REDUCE_TOOLS_UI_AT_TIMELINE_HEADER_PT_layout"
    bl_space_type = 'TIMELINE'
    bl_region_type = 'HEADER'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return "OK"
    
    def draw(self, context):
        
        layout = self.layout

        _drawUis(layout, context, _ADD_TARGET_TIMELINE_HEADER)
        

class DrawOpStepReduceToolsUIAtDopesheetHeader(bpy.types.Header):
    bl_label = "OP Step Reduce Tools"
    bl_idname = "UILER_OP_STEP_REDUCE_TOOLS_UI_AT_DOPESHEET_HEADER_PT_layout"
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'HEADER'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return "OK"
    
    def draw(self, context):
        
        layout = self.layout

        _drawUis(layout, context, _ADD_TARGET_DOPESHEET_HEADER)

class DrawOpStepReduceToolsUIAtDopesheetUI(bpy.types.Panel):
    bl_label = "OP Step Reduce Tools"
    bl_idname = "UILER_OP_STEP_REDUCE_TOOLS_UI_AT_DOPESHEET_UI_PT_layout"
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return "OK"
    
    def draw(self, context):

        layout = self.layout

        _drawUis(layout, context, _ADD_TARGET_DOPESHEET_UI)

        
def register():
    bpy.utils.register_class(OPStepReduceToolsSceneProperties)
    _defProperties()
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_class(OPStepReduceToolsSceneProperties)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

