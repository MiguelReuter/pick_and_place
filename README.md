# Abstract
Python tools for creating an object data base for "Pick and Place" application for UR3 robot.

# Repository architecture 
## Python scripts :
+ **create_data_base.py** : create a data base from UR3 URSripts.
+ **generated_script.py** : generate an URScript with specific objet and specific object target location.

## Directories :
+ **learned_objects_scripts/** : copied URScripts from robot.
+ **object_models/** : contains json file. Each json file represents a specific object.
+ **exported_scripts/** : contains generated URScripts from **generated_script.py**.

# Usage examples

get URScript from UR3 robot, and create all json file :
  python3 create_data_base.py --pull --create
  
clear data base :
  python3 create_data_base.py --clean
    
generate URScript for **box** object, for **A** position (corresponds to [0.0, 0.3] in robot coordinates), and send it to the robot :
  python3 generate_script.py -o object_models/cube.json -p A --push
  