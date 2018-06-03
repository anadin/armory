package armory.logicnode;

import iron.object.Object;
import iron.math.Mat4;
import iron.math.Quat;
import iron.math.Vec4;
import iron.math.Rotator;
import armory.trait.physics.RigidBody;

using iron.math.MathStaticExtension;

class RotateObjectNode extends LogicNode {

	var q = new Quat();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		var rot:Rotator = inputs[2].get();

		if (object == null) return;

		rot = rot.clamp();
		rot = rot.toRadians();

		q.fromEuler(rot.pitch, rot.roll, rot.yaw);
		// q.fromEuler(rot.pitch.toRadians(), rot.roll.toRadians(), rot.yaw.toRadians());

		object.transform.rot.mult(q);
		object.transform.buildMatrix();

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) rigidBody.syncTransform();
		#end

		super.run();
	}
}
