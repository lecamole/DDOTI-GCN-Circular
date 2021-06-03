# DDOTI-GCN-Circular
Code for creating the GCN circular of a DDOTI-Fermi GBR observation

It's only necessary to specify the date of the day when there was a DDOTI observation from a Fermi/GBM alert.
You will also need credentials to access the DDOTI Pipeline webpage.

## A Quick Example
To obtain the circular for a DDOTI observation on Feb 1st 2021:
```
from DDOTI_GCN import gcn_report
gcn_report('20210201')
```
It will print information about the Fermi trigger and the DDOTI observation, as well as the name of the GCN circular file created:
```
Fermi info

Trigger number: 012345678
Trigger time: 2021-02-01 06:38:53.000 UT
Event type: Long GBR
Message type: Final Position 

DDOTI info

DDOTI start: 2021-02-01 06:42:28.000 UT
DDOTI end: 2021-02-01 07:12:28.000 UT
Difference trigger to DDOTI start: 3.58 minutes
Observation time: 30.0 minutes
Center [ra, dec]: 185.180000 , -34.950000
Exp time [sec]: 209.8 , 240.0
Magnitude range (w): 18.33 - 18.66

GCN_circular_2021-02-01_012345678.txt
```
A circular will be created for each of the Fermi alert DDOTI observations available on the specified date.
