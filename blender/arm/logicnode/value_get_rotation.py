import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetRotationNode(Node, ArmLogicTreeNode):
    '''Get rotation node'''
    bl_idname = 'LNGetRotationNode'
    bl_label = 'Get Rotation'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        # self.inputs.new('NodeSocketBool', 'Use Degrees')
        # self.inputs[-1].default_value = True
        # self.outputs.new('NodeSocketVector', 'Rotation')
        self.outputs.new('ArmNodeSocketRotator', 'Rotator')


add_node(GetRotationNode, category='Value')
