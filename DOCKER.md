# DOCKER

This .md is intended to provide basic prerequisites to using the containerised pipeline:

---
## Docker Diagram
```
+------------------+        +------------------+        +------------------+
|  pipeline-part1  |  .json |     OSM3DM       |  .json |  pipeline-part2  |
|   (stages 2-4)   | -----> |  (manual step)   | -----> |   (stages 5-8)   |
|      Docker      |        |    host only     |        |      Docker      |
+------------------+        +------------------+        +------------------+
```
---
## How to run

### Prerequisites
	The entire pipeline is 8-stage but only from stage 2 to stage 8 is covered by the docker image
	Stage 2 - 4, and 5 - 8 respectively, due to an external simulation dependency between stage 4 and stage 5
### Concern over Exclusion of Stage 1
	First stage was not covered due to its dependencies on ROS2 library, which could not be installed with pip.
	Users shall install ROS2 locally then run the first-stage script manually
### Procedures of using the containerised pipeline
    I.      run shell script: `docker compose run pipeline-part1`
    II.     run OSM3DM (proprietary simulation for UWB-based indoor localization developed at TU Chemnitz),
            provide .JSON from stage 4 to OSM3DM
            export reliability-injected .JSON to the repo root directory
            Refer to OSM3DM documentation for full simulation configuration details.
    III.    run shell script: `docker compose run pipeline-part2`
