import simpy.util

class Hardware:
    def __init__(self,env,logfunc):
        self.env=env
        def mylogfunc(msg):
            return(logfunc('HARDWARE '+msg))
        self.log=mylogfunc
        self.orders=[]
        self.status=[]
        self.stopflag=False

    def start(self):
        self.log('starting hardware..')
        self.process=self.env.start(self.run())
        self.log('hardware started.')

    def stop(self):
        self.stopflag=True

    def submit(self,orders):
        self.orders=orders
        self.process.interrupt()

    def get_status(self):
        return(list(set([j for j in self.status if not j.over.triggered])))
   

    def run(self):
        delay=float('inf')
        while not self.stopflag:
            try:
                #do a proper loop for running the jobs according to the orders.
                if len(self.orders)==0:
                    self.log('waiting for orders.' )
                    yield self.env.timeout(delay)
                else:
                    self.log('running some orders.' )
                    yield self.env.timeout(0)
                    while not len(self.orders)==0:
                        wait_time=min(self.orders.values())
                        if not wait_time==0:
                            yield self.env.timeout(wait_time)
                        for j in self.orders:
                            self.orders[j]=self.orders[j]-wait_time
                        for j in self.orders.keys():
                            if self.orders[j]==0:
                                j.start()
                                self.status.append(j)
                                del self.orders[j]
            except simpy.Interrupt:
                self.log('interrupted.' )
        self.log('shutting down.')
        self.env.exit()

class Hardware_slurm:
    def __init__(self,env,logfunc,periodsize,nperiods,decay,vschedule):
        self.env=env
        def mylogfunc(msg):
            return(logfunc('HARDWARE_SLURM '+msg))
        self.log=mylogfunc
        self.periodsize=periodsize
        self.nperiods=nperiods
        self.decay=decay
        self.orders=[]
        self.status=[]
        self.stopflag=False
        self.vschedule=vschedule

    def start(self):
        self.log('starting hardware..')
        self.process=self.env.start(self.run())
        self.process2=self.env.start(self.run2())
        self.log('hardware started.')

    def stop(self):
        self.stopflag=True

    def submit(self,orders):
        self.log('recieving orders')
        self.orders=orders
        self.process.interrupt()

    def get_status(self):
        return(list(set([j for j in self.status if not j.over.triggered])))

    def run(self):
        delay=float('inf')
        while not self.stopflag:
            try:
                #do a proper loop for running the jobs according to the orders.
                if len(self.orders)==0:
                    self.log('waiting for orders.' )
                    yield self.env.timeout(delay)
                else:
                    self.log('running some orders.' )
                    yield self.env.timeout(0)
                    while not len(self.orders)==0:
                        wait_time=min(self.orders.values())
                        if not wait_time==0:
                            yield self.env.timeout(wait_time)
                        for j in self.orders:
                            self.orders[j]=self.orders[j]-wait_time
                        for j in self.orders.keys():
                            if self.orders[j]==0:
                                j.add_callbacks_before(self.add_job_to_slurmtracking)
                                j.add_callbacks_after(self.end_job_in_slurmtracking)
                                j.add_callbacks_after(self.vschedule.update_queue)
                                j.start()
                                self.status.append(j)
                                del self.orders[j]
            except simpy.Interrupt:
                self.log('interrupted.' )
        self.log('shutting down.')
        self.env.exit()

    def update_slurmtracking(self):
        for j in self.trackedjobs:
            if self.periods[0].has_key(j.uid):
                self.periods[0][j.uid]+=j.cores*(self.env.now-self.last_slurmtracking_update)
            else:
                self.periods[0][j.uid]=j.cores*(self.env.now-self.last_slurmtracking_update)

        self.last_slurmtracking_update=self.env.now

    def add_job_to_slurmtracking(self,job):
        #print("addjob call on"+str(job))
        self.log('adding job to slurmtracking')
        self.update_slurmtracking()
        self.trackedjobs.append(job)

    def end_job_in_slurmtracking(self,job):
        #print("endjob call on"+str(job))
        self.log('ending job in slurmtracking')
        self.update_slurmtracking()
        if job in self.trackedjobs:
            self.trackedjobs.remove(job)

    def get_fairshare_factor(self,uid):
        factor=0
        decay=1
        for p in self.periods:
            if p.has_key(uid):
                factor+=decay*p[uid]
                decay*=self.decay
        return(factor)

    def run2(self):
        self.last_slurmtracking_update=self.env.now
        self.periods=[{}]
        self.trackedjobs=[]
        lastrun=0
        while not self.stopflag:
            self.log('period tracker period engaged')
            yield self.env.timeout(self.periodsize)
            self.update_slurmtracking()
            self.periods.insert(0,{})
            if len(self.periods)>=self.nperiods:
                self.periods.pop()
        self.log('period tracker shutting down.')
        self.env.exit()
