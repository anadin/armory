package armory.logicnode;

import iron.math.Rotator;

class RotatorNode extends LogicNode {

	var value = new Rotator();

	public function new(tree:LogicTree, pitch:Null<Float> = null, roll:Null<Float> = null, yaw:Null<Float> = null) {
		super(tree);

		if (pitch != null) {
			addInput(new FloatNode(tree, pitch), 0);
			addInput(new FloatNode(tree, roll), 0);
			addInput(new FloatNode(tree, yaw), 0);
		}
	}

	override function get(from:Int):Dynamic {
		value.pitch = inputs[0].get();
		value.roll = inputs[1].get();
		value.yaw = inputs[2].get();
		return value;
	}

	override function set(value:Dynamic) {
		inputs[0].set(value.pitch);
		inputs[1].set(value.roll);
		inputs[2].set(value.yaw);
	}
}
