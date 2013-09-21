#!/usr/bin/python
'''
Campaign Scheduler Simulator V2.
This is under the DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE v2.0

Usage:
    csim.py <input> <output> <campaign_queue_algorithm> <scheduling_algorithm> <cores> [-v] [--monitor_freq=<frequency>]
    csim.py <input> <output> slurm <period_amount> <period_size> <decay> <scheduling_algorithm> <cores> [-v] [--monitor_freq=<frequency>]


Options:
    -h --help                                      show this help message and exit.
    -v --verbose                                   print extra information and log all data to csim_global.log, csim_users.log, csim_system.log and csim_usersummary.log.
    --monitor_freq=<frequency>                      cron job frequency in discrete time units for miscellaneous logging such as progress bar.[default: 1000000]
    -p <amount> <size> <decay>                     period count ,size and decay for slurm fairsharing. [default: 3 3 3]


campaign queue algorithms available: slurm,ostrich,ostrichadapt,fcfs.
local algorithms available:random_backfill, lpt_backfill, ljf_backfill, ljfp_backfill, greedy. 

'''
#External tool import
import logging
import re
from collections import deque
from docopt import docopt
from simpy import Environment,simulate,Monitor
from simpy.monitoring import PrinterBackend
from Queue import Queue
import yaml
from yaml import CLoader as Loader
#debug
import pdb
#our files import
from Hardware import *
from Common import *
from VirtualAlgorithms import *
from LocalAlgorithms import *
from Monitoring import *

#retrieving arguments
arguments = docopt(__doc__, version='1.0.0rc2')
print(arguments)

#verbose?
if arguments['--verbose']==True:
    print(arguments)

#Getting a simulation environment
env = Environment()

#logger:
global_logger = logging.getLogger('global')
hdlr = logging.FileHandler('csim_global.log')
formatter = logging.Formatter('%(levelname)s %(message)s')
hdlr.setFormatter(formatter)
global_logger.addHandler(hdlr)

#logging level
if arguments['--verbose']==True:
    global_logger.setLevel(logging.INFO)
else:
    global_logger.setLevel(logging.ERROR)

#logging function
def log(msg):
    prefix='%.1f'%env.now
    global_logger.info(prefix+': '+msg)

#cron freq
if  not arguments['--monitor_freq']==None:
    cronfreq=eval(arguments['--monitor_freq'])
else:
    cronfreq=999999999999


#input
log('Opening the yaml file..')
with open(arguments['<input>'],"r") as f:
    yusers=yaml.load(f,Loader=Loader)
log('Done.')

#cores
cores = int(arguments['<cores>'])



#Setting up System

#campaign queue scheduling.
cqalgo=arguments['<campaign_queue_algorithm>']
if cqalgo=='ostrichadapt':
    vschedule=VirtualSchedule_ostrich_adaptative(env,cores,log)
    hardware=Hardware(env,log)
elif cqalgo=='ostrich':
    vschedule=VirtualSchedule_ostrich(env,cores,log)
    hardware=Hardware(env,log)
elif cqalgo=='fcfs':
    vschedule=VirtualSchedule_fcfs(env,log)
    hardware=Hardware(env,log)
elif cqalgo=='shortest':
    vschedule=VirtualSchedule_scf(env,log)
    hardware=Hardware(env,log)
elif arguments['slurm']:
    vschedule=VirtualSchedule_slurm(env,log)
    hardware=Hardware_slurm(env,log,eval(arguments['<period_size>']),eval(arguments['<period_amount>']),eval(arguments['<decay>']),vschedule)
else:
    raise ValueError('unknown virtual algorithm type')

#local scheduling
schalgo=arguments['<scheduling_algorithm>']
if arguments['<scheduling_algorithm>']=='random_backfill':
    sorter=Sorter_random
    lalgo=LocalAlgorithm_backfilling
elif schalgo=='lpt_backfill':
    sorter=Sorter_lpt
    lalgo=LocalAlgorithm_backfilling
elif schalgo=='ljf_backfill':
    sorter=Sorter_ljf
    lalgo=LocalAlgorithm_backfilling
elif schalgo=='ljfp_backfill':
    sorter=Sorter_ljfp
    lalgo=LocalAlgorithm_backfilling
elif schalgo=='greedy':
    sorter=None
    lalgo=LocalAlgorithm_greedy
else:
    raise ValueError('unknown local algorithm type')

system=System(env,vschedule,lalgo,hardware,cores,log,sorter)

users=[]
for uid in yusers.keys():
    campaign_deque=deque()
    cc=0;
    for c in yusers[uid]:
        thinktime=c[0]
        job_list=[Job(env,uid,j['id'],j['cores'],j['reqtime'],j['walltime'],log) for j in c[1]]
        campaign_deque.append(Campaign(env,uid,cc,thinktime,job_list,log))
    users.append(User(env,uid,campaign_deque,system,log))

del yusers

#print(users)

#for user in users:
    #print("User %s with %s campaigns:" %(user.uid,len(user.campaign_deque)))
    #for campaign in user.campaign_deque:
        #print(campaign)
        #for job in campaign.jobs:
            #print(job)

system.start()
for user in users:
    user.start()


if arguments['--verbose'] == True:
    system.set_monitor(system_monitor(system,env,FileBackend(env,'csim_system.log')))
    ubackend=FileBackend(env,'csim_users.log')
    for u in users:
        u.set_monitor(user_monitor(u,env,ubackend))
cronjob_progression = Cronjob_progression(env,cronfreq,users,'csim_usersummary.log')
cronjob_progression.start()

def terminator():
    log('TERMINATOR : waiting for all users to finish.')
    yield simpy.util.all_of([u.over for u in users])
    system.stop()
    if arguments['--verbose'] == True:
        cronjob_progression.stop()
    log('TERMINATOR : all users finished.')
env.start(terminator())

simulate(env)

with open(arguments['<output>'],'w+') as f:
    for user in users:
        for campaign in user.old_campaigns:
            for job in campaign.jobs:
                f.write(job.swfstring()+'\n')

print('-------------SUCCESS----------------')
