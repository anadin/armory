package armory.logicnode;

import iron.object.Object;

class GetRotationNode extends LogicNode {

	// var r = new Rotator();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object:Object = inputs[0].get();

		if (object == null) return null;

		return object.transform.rot.getRotator();
	}
}
