import bpy
import re
import mathutils

from asyncore import poll


#########################################################
# Constants
#########################################################

_SNAP_ACTION_CURSOR_TO_SELECTED = "CURSOR_TO_SELECTED"
_SNAP_ACTION_CURSOR_TO_CENTER = "CURSOR_TO_CENTER"
_SNAP_ACTION_CURSOR_TO_GRID = "CURSOR_TO_GRID"
_SNAP_ACTION_CURSOR_TO_ACTIVE = "CURSOR_TO_ACTIVE"
_SNAP_ACTION_CURSOR_TO_ACTIVE_BONE_TAIL = "CURSOR_TO_ACTIVE_BONE_TAIL"
_SNAP_ACTION_SELECTION_TO_GRID = "SELECTION_TO_GRID"
_SNAP_ACTION_SELECTION_TO_CURSOR = "SELECTION_TO_CURSOR"
_SNAP_ACTION_SELECTION_TO_CURSOR_OFFSET = "SELECTION_TO_CURSOR_OFFSET"
_SNAP_ACTION_SELECTION_TO_ACTIVE = "SELECTION_TO_ACTIVE"
_SNAP_ACTION_SELECTION_TO_ACTIVE_BONE_TAIL = "SELECTION_TO_ACTIVE_BONE_TAIL"

#########################################################
# Global Variables
#########################################################
_is_closure = False
_mirrBones = []

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
def _snapCursor2BoneTail(context):
    tailVec = context.active_pose_bone.tail

    for area in context.screen.areas:
        
        if area.type == "VIEW_3D":
            area.spaces[0].cursor_location = tailVec

def _getCursorLocation(context):

    for area in context.screen.areas:
        
        if area.type == "VIEW_3D":
            return area.spaces[0].cursor_location

def _setCursorLocation(context, vector):

    for area in context.screen.areas:
        
        if area.type == "VIEW_3D":
            area.spaces[0].cursor_location = vector
            return

def _getTargetSelectMap(bones):
    
    ret = {}
    
    for bone in bones:
        
        ret[bone.name] = (bone.select, bone.select_head, bone.select_tail)
    
    return ret

def _getBoneVectorsMap(bones):
    
    ret = {}
    
    for bone in bones:
        
        ret[bone.name] = (bone.vector.copy(), bone.head.copy(), bone.tail.copy())
    
    
    return ret
    

def _getConnectedBoneMap(bones):
    
    ret = {}
    
    for bone in bones:
        ret[bone.name] = bone.use_connect
    
    return ret

def _removeConnectFromBones(bones):
    
    conMap = _getConnectedBoneMap(bones)

    for bone in bones:
        bone.use_connect = False
    
    return conMap

def _revertConnectByMap(bones, conMap):
    
    for bone in bones:
        bone.use_connect = conMap[bone.name]


def _snapSelection2BoneTail(context):
    mode = context.mode
    if mode == "POSE":
        activeBone = context.active_pose_bone
        tailVec = activeBone.tail.copy()
        bones = context.selected_pose_bones
    elif mode == "EDIT_ARMATURE":
        activeBone = context.active_bone
        tailVec = activeBone.tail.copy()
        mirrtailVec = tailVec.copy().reflect(mathutils.Vector((1.0, 0.0, 0.0)))
        bones = bpy.context.active_object.data.edit_bones
    else:
        return
    
    if mode == "POSE":
        isSelect = activeBone.bone.select
        activeBone.bone.select = False
        cursorNow = _getCursorLocation(context).copy()
        _setCursorLocation(context, tailVec)
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
        _setCursorLocation(context, cursorNow)
        activeBone.bone.select = isSelect
    
    if mode == "EDIT_ARMATURE":
    
        isMirror = context.active_object.data.use_mirror_x
        context.active_object.data.use_mirror_x = False
        global _mirrBones
        _mirrBones = []
        tgtSelMap = _getTargetSelectMap(bones)
        tgtVecMap = _getBoneVectorsMap(bones)
        conMap = _removeConnectFromBones(bones)
    
        for bone in bones:
            
            if bone.name == activeBone.name:
                continue
            
            if tgtSelMap[bone.name][0]:
                vec = tgtVecMap[bone.name][0]
                bone.head = tailVec
                bone.tail = bone.head + vec
            else:
                if tgtSelMap[bone.name][1]:
                    bone.head = tailVec
                
                elif tgtSelMap[bone.name][2]:
                    bone.tail = tailVec
                else:
                    continue

            if isMirror:
                mirBone = _getMirrorBone(context, bone)
                if not mirBone:
                    continue
            else:
                continue
              
            if bone.select:
                vec = tgtVecMap[mirBone.name][0]
                mirBone.head = mirrtailVec
                mirBone.tail = mirBone.head + vec
            else:
                if bone.select_head:
                    mirBone.head = mirrtailVec
                if bone.select_tail:
                    mirBone.tail = mirrtailVec
 
        # End
        _revertConnectByMap(bones, conMap)
        context.active_object.data.use_mirror_x = isMirror
        

def _getMirrorBone(context, bone):
    
    if bone.name in _mirrBones:
        return None
    
    nonNumberNm = bone.basename
    num = bone.name.replace(nonNumberNm, "")
    baseNm = ""
    chr = ""
    mirrChr = ""
    isPrefix = False
    isSuffix = False
    isLeft = False
    isRight = False
    
    res = re.match("^(L[._\- ]|Left)(.+)", nonNumberNm, re.IGNORECASE)
    if res:
        chr = res.group(1)
        baseNm = res.group(2)
        isPrefix = True
        isLeft = True

    res = re.match("(.+)(?=([._\- ]L|[._\- ]?Left)$)", nonNumberNm, re.IGNORECASE)
    if res:
        chr = res.group(2)
        baseNm = res.group(1)
        isSuffix = True
        isLeft = True

    res = re.match("^(R[._\- ]|Right)(.+)", nonNumberNm, re.IGNORECASE)
    if res:
        chr = res.group(1)
        baseNm = res.group(2)
        isPrefix = True
        isRight = True

    res = re.match("(.+)(?=([._\- ]R|[._\- ]?Right)$)", nonNumberNm, re.IGNORECASE)
    if res:
        chr = res.group(2)
        baseNm = res.group(1)
        isSuffix = True
        isRight = True

    if not (isPrefix or isSuffix):
        return None
    
    if isPrefix:
        
        if isLeft:
            # Left to Right
            if chr == "Left":
                mirrChr = "Right"
            elif chr == "LEFT":
                mirrChr = "RIGHT"
            elif chr == "left":
                mirrChr = "right"
            else:
                res = re.match("(L)([._\- ])", chr, re.IGNORECASE)
                if res.group(1) == "l":
                    mirrChr = "r" + res.group(2)
                elif res.group(1) == "L":
                    mirrChr = "R" + res.group(2)
        
        if isRight:
            # Right to Left
            if chr == "Right":
                mirrChr = "Left"
            elif chr == "RIGHT":
                mirrChr = "LEFT"
            elif chr == "right":
                mirrChr = "left"
            else:
                res = re.match("(R)([._\- ])", chr, re.IGNORECASE)
                if res.group(1) == "r":
                    mirrChr = "l" + res.group(2)
                elif res.group(1) == "R":
                    mirrChr = "L" + res.group(2)
        
        mirrBoneNm = mirrChr + baseNm + num
    
    if isSuffix:

        if isLeft:
            # Left to Right
            if chr == "Left":
                mirrChr = "Right"
            elif chr == "LEFT":
                mirrChr = "RIGHT"
            elif chr == "left":
                mirrChr = "right"
            else:
                res = re.match("([._\- ])(L)", chr, re.IGNORECASE)
                if res.group(2) == "l":
                    mirrChr = res.group(1) + "r"
                elif res.group(2) == "L":
                    mirrChr = res.group(1) + "R"

        if isRight:
            
            # Right to Left
            if chr == "Right":
                mirrChr = "Left"
            elif chr == "RIGHT":
                mirrChr = "LEFT"
            elif chr == "right":
                mirrChr = "left"
            else:
                res = re.match("([._\- ])(R)", chr, re.IGNORECASE)
                if res.group(2) == "r":
                    mirrChr = res.group(1) + "l"
                elif res.group(2) == "R":
                    mirrChr = res.group(1) + "L"
        
        mirrBoneNm = baseNm + mirrChr + num
        _mirrBones.append(mirrBoneNm)
    
    return context.active_object.data.edit_bones[mirrBoneNm]

#########################################################
# Actions
#########################################################
class SnapCursorAndSelectSnapNoOperation(bpy.types.Operator):
    bl_idname = "uiler.snapcursorandselectsnapnooperation"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        return {'FINISHED'}


class SnapCursorAndSelectSnapByButton(bpy.types.Operator):
    bl_idname = "uiler.snapcursorandselectsnapbybutton"
    bl_label = "Snap"
    bl_options = {'REGISTER', 'UNDO'}
    
    snapaction = bpy.props.StringProperty()
    
    def execute(self, context):
        
        sa = self.snapaction
        
        if sa == _SNAP_ACTION_CURSOR_TO_SELECTED:
            bpy.ops.view3d.snap_cursor_to_selected()
        
        if sa == _SNAP_ACTION_CURSOR_TO_CENTER:
            bpy.ops.view3d.snap_cursor_to_center()
        
        if sa == _SNAP_ACTION_CURSOR_TO_GRID:
            bpy.ops.view3d.snap_cursor_to_grid()
        
        if sa == _SNAP_ACTION_CURSOR_TO_ACTIVE:
            bpy.ops.view3d.snap_cursor_to_active()
        
        if sa == _SNAP_ACTION_CURSOR_TO_ACTIVE_BONE_TAIL:
            _snapCursor2BoneTail(context)
        
        if sa == _SNAP_ACTION_SELECTION_TO_GRID:
            bpy.ops.view3d.snap_selected_to_grid()
        
        if sa == _SNAP_ACTION_SELECTION_TO_CURSOR:
            bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
        
        if sa == _SNAP_ACTION_SELECTION_TO_CURSOR_OFFSET:
            bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
        
        if sa == _SNAP_ACTION_SELECTION_TO_ACTIVE:
            bpy.ops.view3d.snap_selected_to_active()
            
        if sa == _SNAP_ACTION_SELECTION_TO_ACTIVE_BONE_TAIL:
            _snapSelection2BoneTail(context)

        return {'FINISHED'}

class toggleClosureSnapCursorButton(bpy.types.Operator):
    bl_idname = "uiler.toggleclosuresnapcursorbutton"
    bl_label = "label"

    def execute(self, context):
        
        global _is_closure
        
        _is_closure = not _is_closure

        return {'FINISHED'}

#########################################################
# UI
#########################################################
def draw(layout, context):
    
    if _is_closure:
        split = layout.split(1.0)
        row2 = split.row(align=True)
        row2.operator("uiler.toggleclosuresnapcursorbutton", text="Snap Cursor", icon="DISCLOSURE_TRI_RIGHT")
    else:
        split = layout.split(0.1)
        row2 = split.row(align=True)
        row2.scale_x = 1.0
        row = split.row(align=True)
        row.scale_x = 0.5
        row2.operator("uiler.toggleclosuresnapcursorbutton", text="", icon="DISCLOSURE_TRI_DOWN")
        row.operator("uiler.snapcursorandselectsnapnooperation", icon="CURSOR", text=" to")
        row.operator("uiler.snapcursorandselectsnapbybutton", text="S").snapaction = _SNAP_ACTION_CURSOR_TO_SELECTED
        row.operator("uiler.snapcursorandselectsnapbybutton", text="C").snapaction = _SNAP_ACTION_CURSOR_TO_CENTER
        row.operator("uiler.snapcursorandselectsnapbybutton", text="G").snapaction = _SNAP_ACTION_CURSOR_TO_GRID
        row.operator("uiler.snapcursorandselectsnapbybutton", text="A").snapaction = _SNAP_ACTION_CURSOR_TO_ACTIVE
        if context.mode == "POSE":
            row.operator("uiler.snapcursorandselectsnapbybutton", text="A'").snapaction = _SNAP_ACTION_CURSOR_TO_ACTIVE_BONE_TAIL
        
        row.separator()
        row.operator("uiler.snapcursorandselectsnapnooperation", icon="SNAP_ON", text=" to")
        row.operator("uiler.snapcursorandselectsnapbybutton", text="G").snapaction = _SNAP_ACTION_SELECTION_TO_GRID
        row.operator("uiler.snapcursorandselectsnapbybutton", text="C").snapaction = _SNAP_ACTION_SELECTION_TO_CURSOR
        row.operator("uiler.snapcursorandselectsnapbybutton", text="CO").snapaction = _SNAP_ACTION_SELECTION_TO_CURSOR_OFFSET
        row.operator("uiler.snapcursorandselectsnapbybutton", text="A").snapaction = _SNAP_ACTION_SELECTION_TO_ACTIVE
        if context.mode == "POSE" or context.mode == "EDIT_ARMATURE":
            row.operator("uiler.snapcursorandselectsnapbybutton", text="A'").snapaction = _SNAP_ACTION_SELECTION_TO_ACTIVE_BONE_TAIL
