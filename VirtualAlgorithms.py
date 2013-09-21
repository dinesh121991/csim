import simpy

def startwrap(f):
    def func(self,*arg):
        self.log('starting campaign queue algo')
        r=f(self,*arg)
        self.log('campaign queue algo started.')
        return(r)
    return(func)

def submitwrap(f):
    def func(self,campaign):
        self.log('campaign submission: %s.'%campaign)
        r=f(self,campaign)
        return(r)
    return(func)

class VirtualSchedule:
    '''Template for Virtual Schedule.
    It provide standard useless start,stop,submit methods.
    These are mandatory for any virtual schedule.
    startwrap,submitwrap are decorators for logging data.
    usage:
    -inherit VirtualSchedule
    -call super(description,logfunc)
    -define a submit method, and use the decorators for logging.
    -redefine the start,stop methods if you need to. use the start decorators for logging.
    -call directly self.log("blah") to log some info
    '''
    def __init__(self,description,logfunc):
        self.log=lambda msg:logfunc('VIRTUALSCHEDULE/%s '%description+msg)
        self.description=description

    @startwrap
    def start(self,simulator,hardware):
        self.simulator=simulator
        self.hardware=hardware

    def stop(self):
        pass


class VirtualSchedule_scf(VirtualSchedule):
    def __init__(self,env,logfunc):
        self.campaigns=[]
        VirtualSchedule.__init__(self,'SCF',logfunc)

    @submitwrap
    def submit(self,campaign):
        self.campaigns.append(campaign)
        self.simulator.update_virtual_queue(sorted(self.campaigns,key=lambda c: c.workload))

class VirtualSchedule_fcfs(VirtualSchedule):
    def __init__(self,env,logfunc):
        VirtualSchedule.__init__(self,'FCFS',logfunc)

    @submitwrap
    def submit(self,campaign):
        self.simulator.update_virtual_queue([campaign])

class VirtualSchedule_ostrich(VirtualSchedule):
    def __init__(self,env,cores,logfunc):
        self.cores=cores
        self.env=env
        self.system={} #{uid:[[camp1,walltime],[camp2,walltime],..],...}
        self.incoming=None
        self.stopflag=False
        VirtualSchedule.__init__(self,'OSTRICH',logfunc)

    @startwrap
    def start(self,simulator,hardware):
        self.simulator=simulator
        self.process=self.env.start(self.run())

    def stop(self):
        self.stopflag=True

    def run(self):
        delay=float('inf')
        lastrun=0
        while not self.stopflag:
            interrupted=False
            try:
                self.log('entering inactive wait' )
                yield self.env.timeout(delay)
                self.log('inactive wait ended.' )
            except simpy.Interrupt:


                self.log('interrupted with campaign: %s' %self.incoming)
                interrupted=True

            k=len(self.system)

            for uid in self.system.keys():
                ctup=self.system[uid][0]
                ctup[1]=ctup[1]-((self.env.now-lastrun)*self.cores/k)
                if ctup[1]<=1e-4:
                    self.system[uid].remove(ctup)
                    if len(self.system[uid])==0:
                        self.system.pop(uid)

            if interrupted:
                campaign=self.incoming
                if campaign.uid in self.system.keys():
                    self.system[campaign.uid].append([campaign,campaign.workload])
                else:
                    self.system[campaign.uid]=[[campaign,campaign.workload]]

            lastrun=self.env.now
            if not len(self.system)==0:
                delay=float(min([e[0][1] for e in self.system.values()]))*float(k)/float(self.cores)
                self.log('computed delay of %s.' %delay)
            else:
                delay=float("inf")

            vq=sorted([l[0] for l in self.system.values()],key=lambda t:t[1])
            self.log('finished virtual schedule update. updating prio.queue.')
            if not len(vq)==0:
                self.simulator.update_virtual_queue([t[0] for t in vq])

    def submit(self,campaign):
        self.log('campaign submission: %s.' %campaign)
        self.incoming=campaign
        self.process.interrupt()



class VirtualSchedule_slurm(VirtualSchedule):
    def __init__(self,env,logfunc):
        VirtualSchedule.__init__(self,'SLURM',logfunc)
        self.campaignlist=[]

    def sethwref(self,hardware):
        self.hardware=hardware

    @submitwrap
    def submit(self,campaign):
        print("Campaign_Arrival: update virt queue")
        self.campaignlist.append(campaign)
        self.campaignlist=sorted(self.campaignlist,key=lambda c:self.hardware.get_fairshare_factor(c.uid))
        self.simulator.update_virtual_queue(self.campaignlist)

    def update_queue(self,job):
        temp=sorted(self.campaignlist,key=lambda c:self.hardware.get_fairshare_factor(c.uid))
        print(self.campaignlist)
        if not temp==self.campaignlist:
            self.simulator.update_virtual_queue(temp)
            print("Job Termination: update virt queue")
            for c in temp:
                pass
                #print("user %s campaign %s factor %s" %(c.uid,c,self.hardware.get_fairshare_factor(c.uid)))

        else:
            print("Job Termination:NOT update virt queue")

                


class VirtualSchedule_ostrich_adaptative(VirtualSchedule):
    def __init__(self,env,cores,logfunc):
        self.cores=0
        self.env=env
        self.system={} #{uid:[[camp1,walltime],[camp2,walltime],..],...}
        self.incoming=None
        self.stopflag=False
        self.deltacores=0
        VirtualSchedule.__init__(self,'OSTRICH',logfunc)

    @startwrap
    def start(self,simulator,hardware):
        self.simulator=simulator
        self.process=self.env.start(self.run())

    def stop(self):
        self.stopflag=True

    def run(self):
        delay=float('inf')
        lastrun=0
        while not self.stopflag:
            interrupted=False
            try:
                self.log('entering inactive wait' )
                yield self.env.timeout(delay)
                self.log('inactive wait ended.' )
            except simpy.Interrupt:
                if not self.incoming==None:
                    self.log('interrupted with campaign: %s' %self.incoming)
                    interrupted=True
                elif not self.deltacores==0:
                    self.log('interrupted with m adaptation and deltacores of %s'%self.deltacores)
                else:
                    self.log('sleep wakeup.')


            k=len(self.system)

            for uid in self.system.keys():
                ctup=self.system[uid][0]
                ctup[1]=ctup[1]-((self.env.now-lastrun)*self.cores/k)
                if ctup[1]<=1e-4:
                    self.system[uid].remove(ctup)
                    if len(self.system[uid])==0:
                        self.system.pop(uid)

            if interrupted:
                campaign=self.incoming
                if campaign.uid in self.system.keys():
                    self.system[campaign.uid].append([campaign,campaign.workload])
                else:
                    self.system[campaign.uid]=[[campaign,campaign.workload]]

            lastrun=self.env.now
            self.cores+=self.deltacores
            self.deltacores=0

            if not (len(self.system)==0 or self.cores==0):
                delay=float(min([e[0][1] for e in self.system.values()]))*float(k)/float(self.cores)
                self.log('computed delay of %s. from cores value: %s ' %(delay,self.cores))
            else:
                delay=float("inf")

            vq=sorted([l[0] for l in self.system.values()],key=lambda t:t[1])
            self.log('finished virtual schedule update. updating prio.queue.')
            if not len(vq)==0:
                self.simulator.update_virtual_queue([t[0] for t in vq])

    def adapt_m_upwards(self,job):
        self.deltacores+=+job.cores
        self.log("upward m adaptation of %s"%job.cores)
        self.incoming=None
        self.process.interrupt()

    def adapt_m_downwards(self,job):
        self.deltacores+=-job.cores
        self.log("downwards adaptation of %s"%job.cores)
        self.incoming=None
        self.process.interrupt()

    def submit(self,campaign):
        self.log('campaign submission: %s.' %campaign)
        self.incoming=campaign
        for j in campaign.jobs:
            j.add_callbacks_before(self.adapt_m_upwards)
            j.add_callbacks_after(self.adapt_m_downwards)
        self.process.interrupt()


