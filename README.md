# AMMM_Project
## URL
This project is available at: [AMMM Project](https://github.com/HamidL/AMMM_Project)
## Prerequisites
Python version 3.5 is recommended.

NumPy package.

```
pip install numpy
```
## Usefull information

* **OPL model execution:** The model is located at AMMM_Project/OPL/AMMM.mod, it can be manually executed in CPLEX adding any of the instances previously generated or new ones.

* **Python instance generator execution:** To use the instance generator, first modify the configuration file, which is located at AMMM_Project/GreedyGRASP/InstanceGenerator/config.txt. An instance can be generated afterwards executing the InstanceGenerator.py file. The generated instance will be available in the data.dat file.

* **Greedy/GRASP execution:**  To use the solver, first modify the configuration file, which is located at AMMM_Project/GreedyGRASP/config/config.dat. After it has been configured, the solver can be executed in two ways: executing the AMMM_Project/GreedyGRASP/Main.py file (which will use the configuration specified in the configuration file) or executing the AMMM_Project/GreedyGRASP/AllInOne.py file (which will solve the instance using all the configuration combinations possible).

* **Pregenerted files:**  A set of pregenerated files is available at AMMM_Project/Data.

## Authors

* **Hamid Latif Martínez** 
* **Miquel Ferriol Galmés** 

## License

This project is licensed under the MIT License
