/**
 * method4_los.ts
 *
 * Line-of-Sight (LoS) blocked-ratio scoring using Three.js raycasting.
 * Extracted from the M.Sc. thesis simulation:
 * "Robot-Based UWB Localization Testbed and Simulation Environment"
 * TU Chemnitz, 2025 — Ting Tsun Cheng
 *
 * For each anchor, casts a ray toward the tag position and checks whether
 * any obstacle mesh intersects the ray before it reaches the tag.
 * Returns the proportion of blocked anchor-tag pairs as a score (0–100).
 * Higher score = more anchors blocked = less reliable UWB measurement.
 *
 * Background — 4a (obstacle mesh extraction):
 *   The 3D building model loaded via useLoader(GLTFLoader) does not expose
 *   its geometry for raycasting by default. The scene graph must be traversed
 *   to collect all THREE.Mesh objects, which are then passed to this function
 *   as the obstacles array. This traversal is performed in Scene.tsx:
 *
 *     gltf.scene.traverse((child) => {
 *       if (child instanceof THREE.Mesh) meshes.push(child);
 *     });
 *
 *   The collected meshes are lifted to the parent component via the
 *   updateObstacles callback prop and stored in a useRef for use here.
 *
 * Dependencies: three
 *   npm install three
 *
 * Algorithm:
 *   1. For each anchor, construct a ray from anchor toward tag
 *   2. Check intersections against all obstacle meshes
 *   3. If the closest intersection is nearer than the tag, the path is blocked
 *   4. Score = (blocked anchors / total anchors) * 100
 */

import * as THREE from "three";

/**
 * Computes the LoS blocked-ratio score for a given tag position,
 * set of anchor positions, and obstacle meshes.
 *
 * @param tag       - Tag position as THREE.Vector3
 * @param anchors   - Array of anchor positions as THREE.Vector3
 * @param obstacles - Array of THREE.Mesh objects representing obstacles
 *                    (extracted from the loaded GLTF scene graph — see 4a above)
 * @returns Blocked ratio score in range [0, 100].
 *          0   = all anchors have clear line of sight to tag.
 *          100 = all anchors are blocked by obstacles.
 */
export function computeLoSScore(
  tag: THREE.Vector3,
  anchors: THREE.Vector3[],
  obstacles: THREE.Mesh[]
): number {
  let anchorInEffect = anchors.length;

  anchors.forEach((anchorPos) => {
    const ray = new THREE.Raycaster();

    const startPos = anchorPos.clone();
    const endPos = tag.clone();

    // Unit direction vector from anchor toward tag
    const unitDirection = new THREE.Vector3()
      .subVectors(endPos, startPos)
      .normalize();

    // Maximum distance is the anchor-to-tag distance
    const maxDistance = startPos.distanceTo(endPos);

    ray.set(startPos, unitDirection);

    // Check ray against all obstacle meshes (recursive = true for nested objects)
    const intersections = ray.intersectObjects(obstacles, true);

    // Blocked if any intersection exists closer than the tag
    const blocked =
      intersections.length > 0 && intersections[0].distance < maxDistance;

    if (blocked) {
      anchorInEffect -= 1;
    }
  });

  // Score = proportion of blocked anchors, normalised to 0–100
  return ((anchors.length - anchorInEffect) / anchors.length) * 100;
}
