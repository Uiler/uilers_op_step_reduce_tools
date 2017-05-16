import bpy
import re

from asyncore import poll


#########################################################
# Constants
#########################################################
# :see AddonPreferences in init.py
_PROP_COLLECTIONS_PREFIX = "bone_selection_set_grp"

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
def _reNumberPropIdx(context):
    
    user_preferences = context.user_preferences
    prefs = user_preferences.addons[__package__].preferences
    list = eval("prefs." + _PROP_COLLECTIONS_PREFIX)
    
    for idx in range(0, len(list)):
        list[idx].idx = idx
    
    pass

#########################################################
# Actions
#########################################################
####################
# list box function
class AddFunction(bpy.types.Operator):
    bl_idname = "uiler.addboneselectionsetgroupui"
    bl_label = "label"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        user_preferences = context.user_preferences
        prefs = user_preferences.addons[__package__].preferences
        propCollectionNm = _PROP_COLLECTIONS_PREFIX
 
        item = eval("prefs." + propCollectionNm + ".add()")
        item.id = len(eval("prefs." + propCollectionNm))
        item.name = "SelectionSet"
        exec("prefs." + propCollectionNm +"_idx = (len(prefs. " + propCollectionNm + ")-1)")
        
        _reNumberPropIdx(context)

        return {'FINISHED'}

class RemoveFunction(bpy.types.Operator):
    bl_idname = "uiler.removeboneselectionsetgroupui"
    bl_label = "label"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        user_preferences = context.user_preferences
        prefs = user_preferences.addons[__package__].preferences
        propCollectionNm = _PROP_COLLECTIONS_PREFIX
 
        idx = eval("prefs." + propCollectionNm + "_idx")
        eval("prefs." + propCollectionNm + ".remove(idx)")

        _reNumberPropIdx(context)

        return {'FINISHED'}

class UpFunction(bpy.types.Operator):
    bl_idname = "uiler.upboneselectionsetgroupui"
    bl_label = "label"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        user_preferences = context.user_preferences
        prefs = user_preferences.addons[__package__].preferences
        propCollectionNm = _PROP_COLLECTIONS_PREFIX
 
        idx = eval("prefs." + propCollectionNm + "_idx")
        
        if idx < 1:
            return {'FINISHED'}
            
        length = eval("len(prefs." + propCollectionNm + ")")
        eval("prefs." + propCollectionNm + ".move(idx, idx-1)")
        exec("prefs." + propCollectionNm + "_idx -= 1")

        _reNumberPropIdx(context)

        return {'FINISHED'}

class DownFunction(bpy.types.Operator):
    bl_idname = "uiler.downboneselectionsetgroupui"
    bl_label = "label"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        user_preferences = context.user_preferences
        prefs = user_preferences.addons[__package__].preferences
        propCollectionNm = _PROP_COLLECTIONS_PREFIX
 
        idx = eval("prefs." + propCollectionNm + "_idx")
        length = eval("len(prefs." + propCollectionNm + ")")
        
        if idx > length-2:
            return {'FINISHED'}
            
        eval("prefs." + propCollectionNm + ".move(idx, idx+1)")
        exec("prefs." + propCollectionNm + "_idx += 1")

        _reNumberPropIdx(context)

        return {'FINISHED'}

####################
# each items 
class AssignBoneSelectionSetGroupItem(bpy.types.Operator):
    bl_idname = "uiler.assignboneselectionsetgroupitem"
    bl_label = "Assign to group"
#     bl_options = {'REGISTER', 'UNDO'}
    
    target = bpy.props.IntProperty()
    
    def execute(self, context):
        
        user_preferences = context.user_preferences
        prefs = user_preferences.addons[__package__].preferences
        
        for pbone in context.selected_pose_bones:
            prefs.bone_selection_set_grp[self.target].bone_names.add().name = pbone.name
        
        return {'FINISHED'}

class RemoveBoneSelectionSetGroupItem(bpy.types.Operator):
    bl_idname = "uiler.removeboneselectionsetgroupitem"
    bl_label = "Remove from group"
#     bl_options = {'REGISTER', 'UNDO'}
    
    target = bpy.props.IntProperty()
    
    def execute(self, context):
        
        user_preferences = context.user_preferences
        prefs = user_preferences.addons[__package__].preferences

        bone_names = prefs.bone_selection_set_grp[self.target].bone_names
        for boneNm in bone_names:
            
            for pbone in context.selected_pose_bones:

                if boneNm.name == pbone.name:
                    bone_names.remove(bone_names.find(boneNm.name))
        
        return {'FINISHED'}

def _selectDeselectBones(bone, obj, isSelect):
    
    data = obj.data
    bLayers = []
    bIdx = 0
    for isLayer in bone.layers:
        
        if isLayer:
            bLayers.append(bIdx)
        
        bIdx = bIdx + 1
    
    for bLayer in bLayers:
        
        if data.layers[bLayer] and not bone.hide:
            bone.select = isSelect
    
    pass

class SelectBoneSelectionSetGroupItem(bpy.types.Operator):
    bl_idname = "uiler.selectboneselectionsetgroupitem"
    bl_label = "Select bones"
    bl_options = {'REGISTER', 'UNDO'}
    
    target = bpy.props.IntProperty()
    
    def execute(self, context):
        
        user_preferences = context.user_preferences
        prefs = user_preferences.addons[__package__].preferences

        for boneNm in prefs.bone_selection_set_grp[self.target].bone_names:
            
            for bone in context.active_object.pose.bones:
                
                if bone.name == boneNm.name:
                    _selectDeselectBones(bone.bone, context.active_object, True)
                
            
        return {'FINISHED'}

class DeselectBoneSelectionSetGroupItem(bpy.types.Operator):
    bl_idname = "uiler.deselectboneselectionsetgroupitem"
    bl_label = "Deselect bones"
    bl_options = {'REGISTER', 'UNDO'}
    
    target = bpy.props.IntProperty()
    
    def execute(self, context):
        
        user_preferences = context.user_preferences
        prefs = user_preferences.addons[__package__].preferences

        for boneNm in prefs.bone_selection_set_grp[self.target].bone_names:
            
            for bone in context.active_object.pose.bones:
                
                if bone.name == boneNm.name:
                    _selectDeselectBones(bone.bone, context.active_object, False)
        
        return {'FINISHED'}

####################
# Hide
class toggleLayerModeGlobalBoneSelectionSet(bpy.types.Operator):
    bl_idname = "uiler.togglelayermodeglobalboneselectionset"
    bl_label = "label"

    def execute(self, context):
        
        user_preferences = context.user_preferences
        prefs = user_preferences.addons[__package__].preferences

        prefs.isLayerModeGlobalBoneselectionSet = not prefs.isLayerModeGlobalBoneselectionSet
        
        if prefs.isLayerModeGlobalBoneselectionSet:
            for bone in bpy.context.active_object.pose.bones:
                bone.bone.hide = False
        else:
            _updateHideBonesBySelectionSet()

        return {'FINISHED'}

class updateSelectionSetGroupHide(bpy.types.Operator):
    bl_idname = "uiler.updateselectionsetgrouphide"
    bl_label = "label"

    target = bpy.props.IntProperty()

    def execute(self, context):
        
        user_preferences = context.user_preferences
        prefs = user_preferences.addons[__package__].preferences

        prefs.bone_selection_set_grp[self.target].hide = not prefs.bone_selection_set_grp[self.target].hide
        
        _updateHideBonesBySelectionSet()

        return {'FINISHED'}

def _updateHideBonesBySelectionSet():
    
    user_preferences = bpy.context.user_preferences
    prefs = user_preferences.addons[__package__].preferences

    if prefs.isLayerModeGlobalBoneselectionSet:
        return

    ssList = prefs.bone_selection_set_grp
    
    visibleBoneMap = {}
    
    for ss in ssList:
        
        if ss.hide:
            continue
        
        for bone_name in ss.bone_names:
             
             visibleBoneMap[bone_name.name] = True
 

    for bone in bpy.context.active_object.pose.bones:
        
        if bone.name in visibleBoneMap.keys():
             
            bone.bone.hide = False
        
        else:
            
            bone.bone.hide = True
    

####################
# Closure
class toggleClosureGlobalBoneSelectionSet(bpy.types.Operator):
    bl_idname = "uiler.toggleclosureglobalboneselectionset"
    bl_label = "label"

    def execute(self, context):
        
        global _is_closure
        
        _is_closure = not _is_closure

        return {'FINISHED'}

####################
# Lock/Unlock Edit
class toggleLockUnLockEditGlobalBoneSelectionSet(bpy.types.Operator):
    bl_idname = "uiler.togglelockunlockglobalboneselectionset"
    bl_label = "label"

    def execute(self, context):
        
        user_preferences = context.user_preferences
        prefs = user_preferences.addons[__package__].preferences
        prefs.isLockEditGlobalBoneSelectionSet = not prefs.isLockEditGlobalBoneSelectionSet

        return {'FINISHED'}


#########################################################
# UI
#########################################################
class BoneSelectionSetList_items(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        user_preferences = context.user_preferences
        prefs = user_preferences.addons[__package__].preferences
        isLock = prefs.isLockEditGlobalBoneSelectionSet
        
        split = layout.split(0.6)
        row = split.row(align=True)
        split2 = row.split(0.15)
        col1 = split2.row(align=True)
        if item.hide:
            col1.operator("uiler.updateselectionsetgrouphide", emboss=False, text="", icon="RESTRICT_VIEW_ON").target = item.idx
        else:
            col1.operator("uiler.updateselectionsetgrouphide", emboss=False, text="", icon="RESTRICT_VIEW_OFF").target = item.idx
        
        if context.mode != "POSE":
            col1.enabled = False
        
            
        col2 = split2.row(align=True)
        col2.prop(item, "name", text="", emboss=False, translate=False)

        row = split.row(align=True)
        if context.mode != "POSE":
            row.enabled = False

        col = row.column_flow(columns=2, align=True)
        row = col.row(align=True)
        if isLock:
            row.enabled = False
        row.operator("uiler.assignboneselectionsetgroupitem", text="A").target = item.idx
        row.operator("uiler.removeboneselectionsetgroupitem", text="R").target = item.idx
        row = col.row(align=True)
        row.operator("uiler.selectboneselectionsetgroupitem", text="S").target = item.idx
        row.operator("uiler.deselectboneselectionsetgroupitem", text="D").target = item.idx

    def invoke(self, context, event):
        pass   

class BoneNamePropGrp(bpy.types.PropertyGroup):
    '''name = bpy.props.StringProperty() '''
    id = bpy.props.IntProperty()

class BoneSelectionSetPropGrp(bpy.types.PropertyGroup):
    '''name = bpy.props.StringProperty() '''
    id = bpy.props.IntProperty()
#     uid = bpy.props.StringProperty()
    idx = bpy.props.IntProperty()
    bone_names = bpy.props.CollectionProperty(type=BoneNamePropGrp)
    hide = bpy.props.BoolProperty(default=False)

# Main
def draw(layout, context):

    col = layout.column(align=True)
    row = col.row(align=True)
    user_preferences = context.user_preferences
    prefs = user_preferences.addons[__package__].preferences

    if _is_closure:
        row.operator("uiler.toggleclosureglobalboneselectionset", text="", icon="DISCLOSURE_TRI_RIGHT")
    else:
        col_l = row.column()
        col_l.operator("uiler.toggleclosureglobalboneselectionset", text="", icon="DISCLOSURE_TRI_DOWN")

        col_l_c = col_l.column(align=True)
        isLock = prefs.isLockEditGlobalBoneSelectionSet
        col_l_c_r1 = col_l_c.row(align=True)
        if isLock:
            col_l_c_r1.operator("uiler.togglelockunlockglobalboneselectionset", text="", icon="LOCKED")
        else:
            col_l_c_r1.operator("uiler.togglelockunlockglobalboneselectionset", text="", icon="UNLOCKED")

        isLayer = prefs.isLayerModeGlobalBoneselectionSet
        col_l_c_r2 = col_l_c.row(align=True)
        if isLayer:
            col_l_c_r2.operator("uiler.togglelayermodeglobalboneselectionset", text="", icon="MUTE_IPO_ON")
        else:
            col_l_c_r2.operator("uiler.togglelayermodeglobalboneselectionset", text="", icon="MUTE_IPO_OFF")

        if context.mode != "POSE":
            col_l_c_r2.enabled = False

        row2 = row.row()
        col_m = row2.column(align=True)
        propCollectionNm = _PROP_COLLECTIONS_PREFIX
        row3 = col_m.row(align=True)
        row3.template_list("BoneSelectionSetList_items", "", prefs, propCollectionNm, prefs, propCollectionNm + "_idx", rows=3)
    
        row4 = col_m.row(align=True)
        row4.operator("wm.save_userpref", text='Save to "User Preferences"')
#         if isLock:
#             row4.enabled = False

        col_r = row2.column(align=True)
        col_r.row(align=True).operator("pose.select_all", text="", icon="MENU_PANEL").action = 'DESELECT'
        col_r.operator("uiler.addboneselectionsetgroupui", text="", icon="ZOOMIN")
        col_r.operator("uiler.removeboneselectionsetgroupui", text="", icon="ZOOMOUT")
        col_r.separator()
        col_r.operator("uiler.upboneselectionsetgroupui", icon='TRIA_UP', text="")
        col_r.operator("uiler.downboneselectionsetgroupui", icon='TRIA_DOWN', text="")



from bpy.app.handlers import persistent

@persistent
def _initForDraw(dummy):

    user_preferences = bpy.context.user_preferences
    prefs = user_preferences.addons[__package__].preferences
    
    if not prefs.isLayerModeGlobalBoneselectionSet and bpy.context.mode == "POSE":
        _updateHideBonesBySelectionSet()

bpy.app.handlers.load_post.append(_initForDraw)        

