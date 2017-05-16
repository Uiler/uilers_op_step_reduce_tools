import bpy
import re

from asyncore import poll

from . import common

#########################################################
# Constants
#########################################################
_SORT_PRIORITY_A2Z = 0
_SORT_PRIORITY_SPRIT_LR = 1
_SORT_PRIORITY_BONEGROUP = 2

#########################################################
# Global Variables
#########################################################
_sort_priority = [_SORT_PRIORITY_A2Z, _SORT_PRIORITY_SPRIT_LR, _SORT_PRIORITY_BONEGROUP]
_sort_priority_a2z_active = True
_sort_priority_split_lr_active = True
_sort_priority_bonegroup_active = True


def upSortPriority(target):
    idx = _sort_priority.index(target)
    if idx > 0:
        _sort_priority[idx-1], _sort_priority[idx] = _sort_priority[idx], _sort_priority[idx-1]

def downSortPriority(target):
    idx = _sort_priority.index(target)
    if idx < len(_sort_priority) - 1:
        _sort_priority[idx+1], _sort_priority[idx] = _sort_priority[idx], _sort_priority[idx+1]

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
def _getTargetBoneNames(obj):
    
    data = obj.data
    act = obj.animation_data.action
    tgtBoneNms = []

    for bone in data.bones:
      
        bLayers = []
        bIdx = 0
        for isLayer in bone.layers:
            
            if isLayer:
                bLayers.append(bIdx)
            
            bIdx = bIdx + 1
        
        for bLayer in bLayers:
            
            if data.layers[bLayer] and not bone.hide:
                
                if act.fcurves.find('pose.bones["' +  bone.name + '"].location',0):
                    tgtBoneNms.append(bone.name)
                elif act.fcurves.find('pose.bones["' +  bone.name + '"].rotation_quaternion',0):
                    tgtBoneNms.append(bone.name)
                elif act.fcurves.find('pose.bones["' +  bone.name + '"].rotation_euler',0):
                    tgtBoneNms.append(bone.name)
                elif act.fcurves.find('pose.bones["' +  bone.name + '"].scale',0):
                    tgtBoneNms.append(bone.name)
                else:
                    continue

    
    return tgtBoneNms

def _sortChannelsAtoZ(tgtBoneNms):
    
    tgtBoneNms.sort()
    return tgtBoneNms
    
def _sortChannelsSplitLR(tgtBoneNms, act):
    
    neitherList = []
    leftList = []
    rightList = []
    
    for fcurve in act.fcurves:
        res = re.match('pose.bones\["(.+)"\].+', fcurve.data_path)
        try:
            boneNm = res.group(1)
        except:
            # skip non-bone
            continue
    
        if boneNm not in tgtBoneNms or boneNm in neitherList or boneNm in leftList or boneNm in rightList:
            continue
        
        if re.match("^(L[._\- ]|Left)", boneNm, re.IGNORECASE) or re.match(".+(?=([._\- ]L|[._\- ]?Left)(\.[0-9][0-9][0-9])?$)", boneNm, re.IGNORECASE):
            leftList.append(boneNm)
        
        elif re.match("^(R[._\- ]|Right)", boneNm, re.IGNORECASE) or re.match(".+(?=([._\- ]R|[._\- ]?Right)(\.[0-9][0-9][0-9])?$)", boneNm, re.IGNORECASE):
            rightList.append(boneNm)
        
        else:
            neitherList.append(boneNm)
            
    
    newList = []
    newList.extend(neitherList)
    newList.extend(leftList)
    newList.extend(rightList)

    tgtBoneNms = newList
    
    return tgtBoneNms

def _sortChannelsBoneGroups(tgtBoneNms, obj, act):

    bgrpDic = {}
    bgrpNms = []
    noGrpList = []
    for bgrp in obj.pose.bone_groups:
        bgrpDic[bgrp.name] = []
        bgrpNms.append(bgrp.name)
        
    
    pBones = bpy.context.active_object.pose.bones
    for fcurve in act.fcurves:
        res = re.match('pose.bones\["(.+)"\].+', fcurve.data_path)
        try:
            boneNm = res.group(1)
        except:
            # skip non-bone
            continue
    
        if boneNm not in tgtBoneNms or boneNm in noGrpList:
            continue
    
        for bNmList in bgrpDic.values():
            if boneNm in bNmList:
                continue
        
        bIdx = pBones.find(boneNm)
        if bIdx < 0:    
            continue 
        
        if pBones[bIdx].bone_group:
            bgrpDic[pBones[bIdx].bone_group.name].append(boneNm)
    
        else:
            noGrpList.append(boneNm)
    
    newList = []
    newList.extend(noGrpList)
    
    for key in bgrpNms:
        
        newList.extend(bgrpDic[key])
        
    tgtBoneNms = newList
    
    return tgtBoneNms

def _sortChannelsExecuteByBoneNameList(tgtBoneNms, context, obj, act):
    
    tgtBoneNms.reverse()

    bpy.ops.pose.select_all(action='DESELECT')
    bpy.ops.anim.channels_select_all_toggle(invert=False)
    # sort channels
    for boneNm in tgtBoneNms:

        _deselectallBones(context)

        try:
            obj.data.bones.active = obj.data.bones[boneNm]
            obj.pose.bones[boneNm].bone.select = True
            act.groups[boneNm].select = True
            bpy.ops.anim.channels_move(direction='TOP')
        except:
            print("sort skipped:" + boneNm)
    return

def _deselectallBones(context):
    
    obj = context.active_object
    act = obj.animation_data.action
    
    for pBone in obj.pose.bones:
        pBone.bone.select = False

    for grp in act.groups:
        grp.select = False

    return

#########################################################
# Actions
#########################################################
# Sort Action
class SortChannelsAtoZ(bpy.types.Operator):
    bl_idname = "uiler.sortchannelsa2z2"
    bl_label = "Sort Channels A to Z"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        
        obj = context.active_object
        data = obj.data
        act = obj.animation_data.action
        tgtBoneNms = _getTargetBoneNames(obj)

        
        # sort collections
        tgtBoneNms = _sortChannelsAtoZ(tgtBoneNms)
        
        
        _sortChannelsExecuteByBoneNameList(tgtBoneNms, context, obj, act)

        return {'FINISHED'}

class SortChannelsSplitLR(bpy.types.Operator):
    bl_idname = "uiler.sortchannelssplitlr2"
    bl_label = "Sort Channels Split LR"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        
        obj = context.active_object
        data = obj.data
        act = obj.animation_data.action
        tgtBoneNms = _getTargetBoneNames(obj)

        
        # sort collections
        tgtBoneNms = _sortChannelsSplitLR(tgtBoneNms, act)
        
        
        _sortChannelsExecuteByBoneNameList(tgtBoneNms, context, obj, act)

        return {'FINISHED'}

class SortChannelsBoneGroups(bpy.types.Operator):
    bl_idname = "uiler.sortchannelsbonegroups2"
    bl_label = "Sort Channels Bone Groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        
        obj = context.active_object
        data = obj.data
        act = obj.animation_data.action
        tgtBoneNms = _getTargetBoneNames(obj)

        
        # sort collections
        tgtBoneNms = _sortChannelsBoneGroups(tgtBoneNms, obj, act)

        
        _sortChannelsExecuteByBoneNameList(tgtBoneNms, context, obj, act)

        return {'FINISHED'}



class SortChannelsOfBones(bpy.types.Operator):
    bl_idname = "uiler.sortchannelsofbones2"
    bl_label = "Sort Channels Of Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        
        obj = context.active_object
        data = obj.data
        act = obj.animation_data.action
        tgtBoneNms = _getTargetBoneNames(obj)

        
        # sort collections
        for p in _sort_priority:
            if p == _SORT_PRIORITY_A2Z and _sort_priority_a2z_active:

                tgtBoneNms = _sortChannelsAtoZ(tgtBoneNms)

            if p == _SORT_PRIORITY_SPRIT_LR and _sort_priority_split_lr_active:
                
                tgtBoneNms = _sortChannelsSplitLR(tgtBoneNms, act)

            if p == _SORT_PRIORITY_BONEGROUP and _sort_priority_bonegroup_active:

                tgtBoneNms = _sortChannelsBoneGroups(tgtBoneNms, obj, act)
        
        
        _sortChannelsExecuteByBoneNameList(tgtBoneNms, context, obj, act)
        

        return {'FINISHED'}


# Select Action
class selectBonesOfChannels(bpy.types.Operator):
    bl_idname = "uiler.selectbonesofchannels2"
    bl_label = "Select Bones Of Channels"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        
        obj = context.active_object
        data = obj.data
        act = obj.animation_data.action
        tgtBoneNms = []
        
        for bone in data.bones:
          
            bLayers = []
            bIdx = 0
            for isLayer in bone.layers:
                
                if isLayer:
                    bLayers.append(bIdx)
                
                bIdx = bIdx + 1
            
            for bLayer in bLayers:
                
                if data.layers[bLayer] and not bone.hide:


                    schList = common.getBoneFCurvesSeachStrings(bone.name)
                  
                    for sch in schList:
                        
                        fc = act.fcurves.find(sch[0],sch[1])
                        if fc:
                            tgtBoneNms.append(bone.name)
                            break
                    
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.ops.anim.channels_select_all_toggle(invert=False)
        # sort channels
        for boneNm in tgtBoneNms:

            try:
                obj.data.bones.active = obj.data.bones[boneNm]
                obj.pose.bones[boneNm].bone.select = True
                act.groups[boneNm].select = True
            except:
                pass
#                 print("skip select..." + boneNm)
            
        return {'FINISHED'}

def _isExistCurrentKeyframePoint(points, fcurr):
    
    for kfrm in points:
        
        if kfrm.co.x == fcurr:
            
            return True

    return False

class selectBonesOnCurrentKeyPorints(bpy.types.Operator):
    bl_idname = "uiler.selectbonesoncurrentkeypoints"
    bl_label = "Select Bones on current keypoints"
    bl_options = {'REGISTER', 'UNDO'}

    extend = bpy.props.BoolProperty(default=False, subtype='NONE')

    def execute(self, context):

        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        
        fcurr = context.scene.frame_current
        obj = context.active_object
        bones = obj.pose.bones
        data = obj.data
        act = obj.animation_data.action
        tgtBoneNms = []
        
        for bone in bones:
            
            if not common.isVisibleBone(bone.bone):
                continue
            
            
            schList = common.getBoneFCurvesSeachStrings(bone.name)
          
            for sch in schList:
                
                fc = act.fcurves.find(sch[0],sch[1])
                if not fc:
                    continue
                
                if _isExistCurrentKeyframePoint(fc.keyframe_points, fcurr):
                    tgtBoneNms.append(bone.name)
                    break
                
        if not self.extend:
            bpy.ops.pose.select_all(action='DESELECT')
            bpy.ops.anim.channels_select_all_toggle(invert=False)

        for boneNm in tgtBoneNms:

            try:
                obj.data.bones.active = obj.data.bones[boneNm]
                obj.pose.bones[boneNm].bone.select = True
                act.groups[boneNm].select = True
            except:
                pass


        return {'FINISHED'}

class ToggleA2ZSortOptionOnOff(bpy.types.Operator):
    bl_idname = "uiler.togglea2zsortoptiononoff2"
    bl_label = "label"

    def execute(self, context):
        
        global _sort_priority_a2z_active
        _sort_priority_a2z_active = not _sort_priority_a2z_active

        return {'FINISHED'}

class UpA2ZSortOptionPriority(bpy.types.Operator):
    bl_idname = "uiler.upa2zsortoptionpriority2"
    bl_label = "label"

    def execute(self, context):

        upSortPriority(_SORT_PRIORITY_A2Z)

        return {'FINISHED'}

class DownA2ZSortOptionPriority(bpy.types.Operator):
    bl_idname = "uiler.downa2zsortoptionpriority2"
    bl_label = "label"

    def execute(self, context):

        downSortPriority(_SORT_PRIORITY_A2Z)

        return {'FINISHED'}


class ToggleLRSortOptionOnOff(bpy.types.Operator):
    bl_idname = "uiler.togglelrsortoptiononoff2"
    bl_label = "label"

    def execute(self, context):
        
        global _sort_priority_split_lr_active
        _sort_priority_split_lr_active = not _sort_priority_split_lr_active

        return {'FINISHED'}

class UpLRSortOptionPriority(bpy.types.Operator):
    bl_idname = "uiler.uplrsortoptionpriority2"
    bl_label = "label"

    def execute(self, context):

        upSortPriority(_SORT_PRIORITY_SPRIT_LR)

        return {'FINISHED'}

class DownLRSortOptionPriority(bpy.types.Operator):
    bl_idname = "uiler.downlrsortoptionpriority2"
    bl_label = "label"

    def execute(self, context):

        downSortPriority(_SORT_PRIORITY_SPRIT_LR)

        return {'FINISHED'}

class ToggleBoneGroupSortOptionOnOff(bpy.types.Operator):
    bl_idname = "uiler.togglebonegroupsortoptiononoff2"
    bl_label = "label"

    def execute(self, context):
        
        global _sort_priority_bonegroup_active
        _sort_priority_bonegroup_active = not _sort_priority_bonegroup_active

        return {'FINISHED'}

class UpBoneGroupSortOptionPriority(bpy.types.Operator):
    bl_idname = "uiler.upbonegroupsortoptionpriority2"
    bl_label = "label"

    def execute(self, context):

        upSortPriority(_SORT_PRIORITY_BONEGROUP)

        return {'FINISHED'}

class DownBoneGroupSortOptionPriority(bpy.types.Operator):
    bl_idname = "uiler.downbonegroupsortoptionpriority2"
    bl_label = "label"

    def execute(self, context):

        downSortPriority(_SORT_PRIORITY_BONEGROUP)

        return {'FINISHED'}


#########################################################
# UI
#########################################################
def draw(layout, context):

        if context.active_object.type != "ARMATURE":
            return
        
        scene = context.scene

        # sort
        box = layout.box()
        box.label(text="Sort:")
        box.operator("uiler.sortchannelsofbones2", text="Sort Channels(Bones)")

        box2 = box.box()
        box2.label(text="Priorities")
        for p in _sort_priority:
            
            if p == _SORT_PRIORITY_A2Z:
                row = box2.row(align=True)
                _drawA2ZSortPriority(row)

            if p == _SORT_PRIORITY_SPRIT_LR:
                row = box2.row(align=True)
                _drawLRSortPriority(row)

            if p == _SORT_PRIORITY_BONEGROUP:
                row = box2.row(align=True)
                _drawBoneGroupSortPriority(row)

        # select 
        box = layout.box()
        box.label(text="Select:")
        col = box.column(align=True)
        col.operator("uiler.selectbonesofchannels2", text="Select All Bones")
        col.operator("uiler.selectbonesoncurrentkeypoints", text="Bones on current keypoints")
        

def _drawA2ZSortPriority(row):
    
    row.operator("uiler.togglea2zsortoptiononoff2", text="", icon='RESTRICT_VIEW_OFF' if _sort_priority_a2z_active else 'RESTRICT_VIEW_ON')
    row.operator("uiler.sortchannelsa2z2", text="A to Z")
    row.operator("uiler.upa2zsortoptionpriority2", text="", icon="TRIA_UP")
    row.operator("uiler.downa2zsortoptionpriority2", text="", icon="TRIA_DOWN")
    
    return

def _drawLRSortPriority(row):
    
    row.operator("uiler.togglelrsortoptiononoff2", text="", icon='RESTRICT_VIEW_OFF' if _sort_priority_split_lr_active else 'RESTRICT_VIEW_ON')
    row.operator("uiler.sortchannelssplitlr2", text="Split LR")
    row.operator("uiler.uplrsortoptionpriority2", text="", icon="TRIA_UP")
    row.operator("uiler.downlrsortoptionpriority2", text="", icon="TRIA_DOWN")
    
    return

def _drawBoneGroupSortPriority(row):

    row.operator("uiler.togglebonegroupsortoptiononoff2", text="", icon='RESTRICT_VIEW_OFF' if _sort_priority_bonegroup_active else 'RESTRICT_VIEW_ON')
    row.operator("uiler.sortchannelsbonegroups2", text="Bone Group")
    row.operator("uiler.upbonegroupsortoptionpriority2", text="", icon="TRIA_UP")
    row.operator("uiler.downbonegroupsortoptionpriority2", text="", icon="TRIA_DOWN")
    
    return


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

