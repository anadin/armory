import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RotatorNode(Node, ArmLogicTreeNode):
    '''Rotator node'''
    bl_idname = 'LNRotatorNode'
    bl_label = 'Rotator'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('NodeSocketFloat', 'Pitch (X)')
        self.inputs.new('NodeSocketFloat', 'Roll (Y)')
        self.inputs.new('NodeSocketFloat', 'Yaw (Z)')
        
        self.outputs.new('ArmNodeSocketRotator', 'Rotator')
        # self.outputs.new('NodeSocketFloat', 'Rotator')

add_node(RotatorNode, category='Variable')
