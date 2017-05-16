import bpy


#########################################################
# Constants

#########################################################
# Global Variables
#########################################################

#########################################################
# Functions
#########################################################
# bone: bpy.context.active_object.pose.bones[n].bone
def isVisibleBone(bone):
    
    if not bone:
        return False
    
    data = bone.id_data.data
    
    bLayers = []
    bIdx = 0
    for isLayer in bone.layers:
        
        if isLayer:
            bLayers.append(bIdx)
        
        bIdx = bIdx + 1
    
    for bLayer in bLayers:
        
        return data.layers[bLayer] and not bone.hide
    
    return False

# bones: bpy.context.active_object.pose.bones
def getVisibleMapOfPoseBone(bones):
    
    ret = {}
    
    for bone in bones:
        
        ret[bone.name] = bone.bone.select
    
    return ret

# bones, map: see getVisibleMapOfPoseBone(bones)
def revertBoneVisibleByMap(bones, map):
    
    if not map:
        return
    
    for key in map.keys():
        bones[key].bone.select = map[key]
        

# initialize driver
def initializeDriver(driver):

    # remove default modifier
    removeDriverModifiers(driver.modifiers)
    
    d = driver.driver
    # driver type
    d.type = 'SUM'
    
    # remove Variables
    removeDriverVariables(d.variables)

# remove F-Curve Modifiers
def removeDriverModifiers(mods):
    for mod in mods:
        mods.remove(mod)

# remove driver Valiables
def removeDriverVariables(variables):
    for vars in variables:
        vars.remove(vars)
        

def isActiveAddonFunctionByName(name):

    user_preferences = bpy.context.user_preferences
    prefs = user_preferences.addons[__package__].preferences

    list = []
    list.extend(prefs.fns_3dview_header)
    list.extend(prefs.fns_3dview_tools)
    list.extend(prefs.fns_3dview_ui)
    list.extend(prefs.fns_dopesheet_header)
    list.extend(prefs.fns_dopesheet_ui)
    list.extend(prefs.fns_timeline_header)
    for func in list:
        if func.name == name:
            return True
        
    return False


def getBoneFCurvesSeachStrings(bonename):

    ret = []
    
    pathLoc = 'pose.bones["' +  bonename + '"].location'
    ret.append((pathLoc, 0))
    ret.append((pathLoc, 1))
    ret.append((pathLoc, 2))
    
    pathRotq = 'pose.bones["' +  bonename + '"].rotation_quaternion'
    ret.append((pathRotq, 0))
    ret.append((pathRotq, 1))
    ret.append((pathRotq, 2))
    ret.append((pathRotq, 3))
    
    pathRote = 'pose.bones["' +  bonename + '"].rotation_euler'
    ret.append((pathRote, 0))
    ret.append((pathRote, 1))
    ret.append((pathRote, 2))
    
    pathSca = 'pose.bones["' +  bonename + '"].scale'
    ret.append((pathSca, 0))
    ret.append((pathSca, 1))
    ret.append((pathSca, 2))

    return ret

#########################################################
# Properties
#########################################################

#########################################################
# Actions
#########################################################

#########################################################
# UI
#########################################################
