import bpy

bl_info = {
    "name": "blendmotion",
    "author": "coord.e <me@coord-e.com>",
    "version": (0, 1),
    "blender": (2, 7, 9),
    "location": "",
    "description": "convert animation to robot motion",
    "warning": "You may need phobos plugin to be installed on your system",
    "wiki_url": "",
    "tracker_url": "https://github.com/DeepL2/blendmotion",
    "category": "",
}

def make_armature(name):
    """
        name: str
    """
    bpy.ops.object.add(type='ARMATURE', enter_editmode=True)
    amt = bpy.context.object
    amt.name = name
    return amt

def calc_pos(o):
    """
        o: Object
    """
    return o.data.bones[0].head + o.location

def make_bone(o, amt):
    """
        o: Object
        amt: Armature
    """
    b = amt.data.edit_bones.new('Bone')
    b.head = calc_pos(o.parent)
    b.tail = calc_pos(o)
    return b

def attach_parent(parent, child):
    """
        parent: EditBone
        child: EditBone
    """
    child.parent = parent

def make_bones_recursive(o, amt):
    """
        o: Object
        amt: Armature
    """
    parent_bone = make_bone(o, amt)
    for child in o.children:
        child_bone = make_bones_recursive(child, amt)
        attach_parent(parent_bone, child_bone)
    return parent_bone

amt = make_armature("Main")
make_bone_rec(bpy.data.objects["root_obj"], amt)
