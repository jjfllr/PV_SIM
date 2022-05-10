# PV_SIM
homework from TMH

This program emulates the consumption of a household and a photovoltaic generator
the household emulation is given by a Perlin Noise function [1], given by the Perlin-noise
library hosted in PyPi [2] and the photovoltaic generator is modeled with 3 functions;
Both models have a random noise added to simulate some perturbances in the electrical network.

In this simulation, the household consumes energy and sends a message to the generator, using
RabbitMQ as a broker. This way the generator can see how much energy it produced and log the
relevant data in a log file, if not named the logs will appear in the console.

The simulation uses 3 threads, one running the application, one simulating the household and
a final one simulating the generator. This in order to parallel the household and the generator
as different entities.

Time can be both simulated or be taken from the real world. A simulated day (86400 seconds)
should take 10 minutes.

configurations.py holds the configuration parameters of the models, as well as the data
required to make the connection to the RabbitMQ server, ideally running in localhost.

RUNNING THE PROGRAM

  Please be shure that a RabbitMQ server is running in the host machine or modify configurations.py
  accordingly. The default credentials for RabbitMQ are hardcoded and are set by the pika.PlainCredentials()
  method. They can be changed in the configurations.py file.

  To run the program simply run the main.py script, an interactive menu will ask for
  the simulation parameters. The execution path should be in the $PYTHON_PATH variable
  and the folder structure be maintained.

  At first the program will ask if the user wants to simulate or run in real time.
  the mode is choose by the Highlighted letter (S or s for simulated, R or r for
  real time)

  Then will ask for the starting time for the simulation, in an HH:MM:SS format.
  this step is omitted if real time was chose.

  The program will ask for a duration for the simulation, this should be seconds.

  It will ask for a name for both the household and the generator, these can be omitted.

  Finally will ask for a name for the logfile, if not given, the logger will output to
  the console.




















[1] https://en.wikipedia.org/wiki/Perlin_noise
[2] https://pypi.org/project/perlin-noise/
