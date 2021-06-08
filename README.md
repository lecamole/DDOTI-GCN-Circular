# DDOTI-GCN-Circular
Code for creating the GCN circular of a DDOTI-Fermi GBR observation

It's only necessary to specify the date of the DDOTI observation of a Fermi GBM alert.  
You will also need the GCN circular template and the credentials to access the DDOTI Pipeline webpage.

## A Quick Example
To obtain the circular for a DDOTI observation on Feb 1st 2021:
```
from DDOTI_GCN import gcn_report
gcn_report('20210201')
```
You will need to type the user and the password to access the pipeline.  
It will print information about the Fermi trigger and the DDOTI observation, which is the same data that is added to the template; as well as the name of the GCN circular file created:

> Fermi info
> 
> Trigger number: 012345678  
> Trigger time: 2021-02-01 01:02:03.000 UT  
> Event type: Long GRB  
> Message type: Final Position  
>   
> DDOTI info  
> 
> DDOTI start: 2021-02-01 04:05:06.000 UT  
> DDOTI end: 2021-02-01 07:08:09.000 UT  
> Difference trigger to DDOTI start: 1.23 minutes  
> Observation time: 12.3 minutes  
> Center [ra, dec]: 123.456 , -78.910000
> Grid size: 3 x 2
> Region size [ra, dec]: 20.4 , 20.4
> Instrumental fields: 6 (400 deg)  
> Exp time [sec]: 111.1 , 222.2  
> Magnitude range (w): 12.34 - 56.78  
> 
> GCN_circular_2021-02-01_012345678.txt  

A circular will be created for each of the Fermi alert DDOTI observations available on the specified date.
