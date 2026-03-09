/**
 * method3_pdop.ts
 *
 * PDOP-based anchor geometry reliability scoring.
 * Extracted from the M.Sc. thesis simulation:
 * "Robot-Based UWB Localization Testbed and Simulation Environment"
 * TU Chemnitz, 2025 — Ting Tsun Cheng
 *
 * Given a tag position and a set of anchor positions, computes a
 * normalised PDOP score (0–100) indicating UWB positioning reliability.
 * Lower score = better anchor geometry = more reliable positioning.
 *
 * Algorithm:
 *   1. Filter anchors within 30m of the tag
 *   2. Build observation matrix H (unit vectors from tag to each anchor)
 *   3. Compute pseudoinverse of H^T * H via Moore-Penrose (math.js pinv)
 *   4. PDOP = sqrt(Q[0][0] + Q[1][1] + Q[2][2])
 *   5. Clamp to 6 and normalise to 0–100
 *
 * Dependencies: mathjs
 *   npm install mathjs
 */

import * as math from "mathjs";

/**
 * Represents a 3D position as [x, y, z].
 */
type Position3D = [number, number, number];

/**
 * Computes a normalised PDOP score for a given tag position and
 * set of anchor positions.
 *
 * @param tag       - Tag position [x, y, z] in metres
 * @param anchors   - Array of anchor positions [x, y, z] in metres
 * @param proximity - Maximum anchor-to-tag distance to include (default: 30m)
 * @returns Normalised PDOP score in range [0, 100].
 *          100 = worst geometry or fewer than 4 anchors in range.
 *          0   = perfect geometry (PDOP = 0, theoretical minimum).
 */
export function computePDOP(
  tag: Position3D,
  anchors: Position3D[],
  proximity: number = 30
): number {
  // Filter anchors within proximity range
  const nearAnchors = anchors.filter(
    (anchor) => Number(math.distance(anchor, tag)) <= proximity
  );

  // PDOP is undefined with fewer than 4 anchors — return worst score
  if (nearAnchors.length < 4) {
    return 100;
  }

  // Euclidean distance from tag to each anchor
  const r_set: number[] = nearAnchors.map((anchor) =>
    Number(math.distance(tag, anchor))
  );

  // Observation matrix H: each row is the unit vector from tag to anchor
  const matrix_H: number[][] = nearAnchors.map((anchor, i) =>
    math.dotDivide(math.subtract(anchor, tag), r_set[i]) as number[]
  );

  // Q = pseudoinverse of H^T * H (Moore-Penrose)
  const matrix_H_mat = math.matrix(matrix_H);
  const matrix_Q_mat = math.pinv(
    math.multiply(math.transpose(matrix_H_mat), matrix_H_mat)
  );
  const matrix_Q = matrix_Q_mat.toArray() as number[][];

  // PDOP = sqrt of trace of Q (x, y, z components only)
  let PDOP = Math.sqrt(matrix_Q[0][0] + matrix_Q[1][1] + matrix_Q[2][2]);

  // Clamp and normalise to 0–100
  PDOP = Math.min(PDOP, 6);
  return (PDOP * 100) / 6;
}
