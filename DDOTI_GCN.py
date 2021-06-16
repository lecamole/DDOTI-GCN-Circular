# -*- coding: utf-8 -*-
"""
@author: lecamole
"""

import getpass
import shutil
import requests
import lxml.html as lh
import pandas as pd
from astropy.time import Time

def lines(data,delimiter):
    '''
    Takes a string and divides it in lines according to the specified delimiter,
    creating a list of strings. It also cleans it up of white spaces.

    Parameters
    ----------
    data : str object
        String with a certain delimiter
    delimiter : str object
        Character delimiting lines in the string.

    Returns
    -------
    lines : list
        List of lines.

    '''
    lines = (line.rstrip() for line in data)
    lines = (line.split(delimiter, 1)[0] for line in lines)
    lines = (line.rstrip() for line in lines)
    lines = (line.lstrip() for line in lines)
    lines = (line for line in lines if line)
    lines = list(lines)
    return lines

def bitacora_fermi():
    '''
    Takes the table of Fermi GBRs from the webpage    
    Returns
    -------
    df : Dataframe with all of the Fermi GBR alerts since Sept 2019.
        '''
    #Retrieve html page
    url = 'https://gcn.gsfc.nasa.gov/fermi_grbs.html'
    df=pd.read_html(url, header=1)[0]
    #drop Comments column and all events before Sept 1st 2019
    df = df.drop('Comments',axis=1)
    df.drop(df[df['Date'] < '19/09/01'].index, inplace = True)
    #reverse index so most recent trigger have bigger indexes
    df = df.iloc[::-1]
    df.iloc[:] = df.iloc[::-1].values
    
    return df

def timeconver(time):
    if  60 <= time < 3600:
        t=round(time/60,2)
        unit='minutes'
    elif time >= 3600:
        t=round(time/3600,2)
        unit='hours'
    else:
        t=round(time,2)
        unit='seconds'
    #timeunit=str(time)+' '+unit
    return t,unit

def gcn_report(Date):
    '''
Takes the date of a DDOTI observation of a Fermi GBM event
and returns the GCN circular text file of said event.
Parameters
----------
Date : str object
Date when the DDOTI observation took place in the format YYYYMMDD.

Returns
-------
GCN_circular_DATE_[triggernumber].txt: txt file
Text file of the GCN report for a GBR DDOTI observation.

'''
    #Asks for credentials to access the DDOTI Pipeline webpage
    u=getpass.getpass(prompt='User:')
    p=getpass.getpass(prompt='Password:')
    page=requests.get('http://transients.astrossp.unam.mx/ddoti/direct.html',auth=(u,p))
    doc = lh.fromstring(page.content)
    print(page,'\n')
    archive = (doc.text_content()).split('\n')    
    archive=lines(archive,'        ')
    archive=(line.lstrip() for line in archive)
    archive=list(archive)   
    #Obtains the list of DDOTI observations from that date
    Date=Date+':'
    for num, line in enumerate(archive,0):
        if Date in line:
            datee=archive[num].rstrip(':')
            obs=archive[num+1]
            obs=obs.split('     ')
            obs=(line.lstrip() for line in obs)
            obs=list(obs)
            break
    #Obtains the list of DDOTI observations that correspond to a Fermi GBM trigger
    trignum=[]
    ddoti_data=[]
    for num, line in enumerate(obs,0):
        if '1002' in line: 
            fermi_obs=obs[num].split('/')
            ddoti_data.append(fermi_obs[0])
            trignum.append(fermi_obs[1])
    
    if any(trignum) is False:
        print(Date[:-1])
        print('No Fermi ID on that date.')
        return
            
    bit=bitacora_fermi()
    bit=bit.drop_duplicates('TrigNum',keep='first')
    
    for num,line in enumerate(trignum,0):
        url='http://transients.astrossp.unam.mx/ddoti/'+datee+'/'+ddoti_data[0]+'/'+trignum[num]+'/'
        page_visits=requests.get(url, auth=(u,p))
        #print(url)
        doc_visits = lh.fromstring(page_visits.content)  
        visits = (doc_visits.text_content()).split('\n')        
        exptime=[]
        visit=[]
        for idx,line in enumerate(visits,0):
            if 'Note:' in line:
                center=line
                center=center[center.index('at:')+4:]
                center=center.strip()
                center_ra,center_dec=center.split(' , ')
            if 'Limiting' in line:
                w=visits[idx]
                w=w[w.index(': ')+2:w.index(r" (")]
                w_min,w_max=w.split(' - ')
            if 'Visit' in line:
                visit.append(line)
                # exp=visits[idx][visits[idx].index('/')-5:visits[idx].index('/')+5]
                # exp=exp.split('/')
                # exptime.append(exp)
        
        # exptime = [item for sublist in exptime for item in sublist]
        # exptime = [line.strip(' ') for line in exptime]
        # exp_min=min(exptime)
        # exp_max=max(exptime)
        
        visit_df=[line.split() for line in visit]
        visit_df=pd.DataFrame(visit_df,columns=('Visit','#',':','File','Exposure','RA','Dec'))
        
        exptime=[line.split('/') for line in visit_df['Exposure']]
        exptime=[item for sublist in exptime for item in sublist]
        exptime=[float(i) for i in exptime]
        exp_min=min(exptime)
        exp_max=max(exptime)
        
        msg_type=bit.loc[bit['TrigNum'] == int(trignum[num]), 'MesgTypeGBMLAT'].iloc[0]
        msg_type=msg_type[4:]        
        #ddoti times
        #date
        ddate=visit[0][visit[0].index('_')+1:visit[0].index('T')]
        ddate=ddate[0:4]+'-'+ddate[4:6]+'-'+ddate[6:8]
        #start time
        startime=visit[0][visit[0].index('T')+1:visit[0].index('_C')]
        startime=startime[0:2]+':'+startime[2:4]+':'+startime[4:6]
        startime = ddate +' '+ startime
        startime=Time(startime,scale='ut1')
        #endtime
        
        error=bit.loc[bit['TrigNum'] == int(trignum[num]), 'Error[deg][arcmin]'].iloc[0]
        
        if error < 2:
            grid='2 x 1'
            inst='2'
            tot_field = '150'
            ra_reg= '13.6'
            dec_reg= '10.2'
            url=url+'1/current_C0.html'
        elif 2 >= error < 4:
            grid='2 x 2'
            inst='4'
            tot_field = '300'
            ra_reg= '13.6'
            dec_reg= '20.4'
            url=url+'3/current_C0.html'
        elif error >= 4:
            grid='3 x 2'
            inst='6'
            tot_field = '400'
            ra_reg= '20.4'
            dec_reg= '20.4'
            url=url+'5/current_C0.html'
        
        # grid=len(visit)/6
        # if  grid == 1:
        #     url=url+'0/current_C0.html'
        # elif grid == 2:
        #   pass            
        # elif grid == 3:
        #     url=url+'2/current_C0.html'
        # elif grid == 4:
        #   pass
        # elif grid == 5:
        #     url=url+'4/current_C0.html'
        # elif grid == 6:
            
            
        page_endtime=requests.get(url,auth=(u,p))
        #print(url,'\n')
        doc_endtime = lh.fromstring(page_endtime.content)
        endtime = (doc_endtime.text_content()).split('\n\n')[1]
        endtime=endtime[endtime.index(']')-6:endtime.index(']')]
        endtime=endtime[0:2]+':'+endtime[2:4]+':'+endtime[4:6]
        endtime= ddate+' '+endtime
        endtime=Time(endtime,scale='ut1')
                
        #fermi times
        datte=bit.loc[bit['TrigNum'] == int(trignum[num]), 'Date'].iloc[0]
        datte='20' + datte.replace('/','-')
        trigtime=bit.loc[bit['TrigNum'] == int(trignum[num]), 'Time UT'].iloc[0]
        trigtime=trigtime[:-3]
        trigtime=datte+' '+trigtime
        trigtime=Time(trigtime,scale='ut1')
        
        url_fermi = 'https://gcn.gsfc.nasa.gov/other/' + trignum[num] + '.fermi'
        page_fermi = requests.get(url_fermi)
        doc_fermi = lh.fromstring(page_fermi.content)
        notice_fermi = (doc_fermi.text_content().split('\n'))
        doc_fermi=doc_fermi.text_content()
        notice_fermi=lines(notice_fermi,'///')
        
        # if 'MOST_LIKELY:' in doc_fermi:
        # #runs through all the lines in notice
        #     for idx,line in enumerate(notice_fermi, 0):
        #         #searches for MOST LIKELY in each of the lines in notice,
        #         #stops once it finds it
        #         if 'MOST_LIKELY:' in line:
                    
        #             (tmp) = line.split(':  ')
        #             event = tmp[1]
        #             break
        # #if no 'MOST LIKELY' in doc, it adds a NO EVENT to the event list
        # else:
        #     event='no event specified'
    
        if 'This is likely' in doc_fermi:
            #runs through all the lines in notice
            for idx,line in enumerate(notice_fermi, 0):
                #searches for this is likely in each of the lines in notice,
                #stops once it finds it
                if 'This is likely' in line:
                    (tmp) = line.split('a')
                    grb = tmp[1]
                    grb=grb.rstrip('.')
                    grb=grb[1:-4]
                    break
        #if no 'MOST LIKELY' in doc, it adds a NO EVENT to the event list            
        else:
            grb='NO DATA'
            
        #time deltas       
        trigdelta=(startime - trigtime).sec #dotti start time minus trigger time
        ddelta=(endtime-startime).sec #ddoti starttime minus endtime
        endobs= round(ddelta + trigdelta,2)
        
        trigdelta,unit=timeconver(trigdelta)
        ddelta,units=timeconver(ddelta)       
        endobs, unit_e = timeconver(endobs)    
        
        print('Fermi info\n')
        print('Trigger number:', trignum[num])
        print('Trigger time:',trigtime, 'UT')
        print('Event type:', grb + ' GBR' )
        print('Message type:', msg_type,'\n')      
        print('DDOTI info\n')
        print('DDOTI start:',startime,'UT')
        print('DDOTI end:',endtime, 'UT')
        print('Difference trigger to DDOTI start:',trigdelta, unit)
        print('Observation time:',ddelta, units)
        print('Center [ra, dec]:',center)
        print('Grid size:',grid)
        print('Region size [ra, dec]:',ra_reg,',',dec_reg)
        print('Instrumental fields:',inst,'('+tot_field+' deg)')
        print('Exp time [sec]:',exp_min,',',exp_max)
        print('Magnitude range (w):',w,'\n')
        
        file=shutil.copy('GCN_circular_template.txt', 
                         'GCN_circular'+'_'+ddate+'_'+trignum[num]+'.txt')
        print(file)
        print('\n////////////////////////////////////////////\n')
        
        with open(file,'r+') as circular:
            text=circular.read()
            text=text.replace('TRIGNUM',trignum[num])
            text=text.replace('STARTRIG',str(trigdelta)+' '+unit)
            text=text.replace('ENDTRIG',str(endobs)+' '+unit_e)
            text=text.replace('DATE', ddate.replace('-','/'))
            text=text.replace('START', str(startime).split(' ')[1])
            text=text.replace('END', str(endtime).split(' ')[1])
            text=text.replace('MAGmin',w_min)
            text=text.replace('MAGmax',w_max)
            text=text.replace('RIGHTAS',center_ra)
            text=text.replace('DECLI',center_dec)
            text=text.replace('MIN_exptime',str(exp_min))
            text=text.replace('MAX_exptime',str(exp_max))
            text=text.replace('MSGTYPE',msg_type)
            text=text.replace('TYPE',grb)
            text=text.replace('GRID_SIZE',grid)
            text=text.replace('INST',inst)
            text=text.replace('TOT_FIELD',tot_field)
            text=text.replace('RA_REG',ra_reg)
            text=text.replace('DEC_REG',dec_reg)
            circular.seek(0)
            circular.write(text)
            
        print(text)
        print('\n////////////////////////////////////////////\n') 
