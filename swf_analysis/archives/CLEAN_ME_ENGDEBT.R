library(ggplot2)
library(epicalc)

source('campaign_scheduling_metrics.R')
source('color.R')
source('analysis.R')
source('utilization.R')
source('standard_label.R')
source('campaign_detection.R')

df2ed<-function(data_ostrich,data_fcfs,assoc){
	

	Co<-campaign_detection_ed(data_ostrich)
	Cf<-campaign_detection_ed(data_fcfs)
	assoc=read.table(assoc)
	names(assoc)=c("user","category")

	shortlong=function(i){
		if (i==1)
			return("Long")
		if (i==0)
			return("Short")
	}
	
	m=max_cores(data_ostrich)	
	print(paste("OEUOEUOEUEOQKKK:::::",m))
	Uo=max_stretches(Co,m)
	Uo$category=lapply(assoc[Uo$user,]$category,shortlong)
	Uf=max_stretches(Cf,m)
	Uf$category=lapply(assoc[Uf$user,]$category,shortlong)
	print(Uo)
	print(Uf)

	ostrich_max_mean_short=cbind("Ostrich","Short",ci(Uo[Uo$category=="Short",]$max_stretch))
	ostrich_max_mean_long=cbind("Ostrich","Long",ci(Uo[Uo$category=="Long",]$max_stretch))
	fcfs_max_mean_short=cbind("FCFS","Short",ci(Uf[Uf$category=="Short",]$max_stretch))
	fcfs_max_mean_long=cbind("FCFS","Long",ci(Uf[Uf$category=="Long",]$max_stretch))
	
	colnames(ostrich_max_mean_short)=c("Algorithm","category","n","max_stretch","sd","se","lowerci","upperci")
	colnames(ostrich_max_mean_long)=c("Algorithm","category","n","max_stretch","sd","se","lowerci","upperci")
	colnames(fcfs_max_mean_short)=c("Algorithm","category","n","max_stretch","sd","se","lowerci","upperci")
	colnames(fcfs_max_mean_long)=c("Algorithm","category","n","max_stretch","sd","se","lowerci","upperci")

	print(rbind(ostrich_max_mean_short,ostrich_max_mean_long,fcfs_max_mean_short, fcfs_max_mean_long))
	Limits=c("Short","Long")
        #ggplot(U,aes(x = category,y=max_stretch)) +geom_bar(aes(fill = Algorithm), position = "dodge")+ylab("Max Stretch Average")+xlab("User Job lenght type")+ scale_fill_manual(values=c("#373332","#736F6E" ))+scale_x_discrete(limits=Limits)

	U=rbind(ostrich_max_mean_short,ostrich_max_mean_long,fcfs_max_mean_short, fcfs_max_mean_long)
		

	ggplot(U, aes(x=category, y=max_stretch, fill=Algorithm)) + 
    geom_bar(position=position_dodge(), stat="identity") +
    geom_errorbar(aes(ymin=lowerci, ymax=upperci),
                  width=.2,                    # Width of the error bars
                  position=position_dodge(.9))+ylab("Max Stretch Mean, 95% confidence interval")+xlab("User Job length profile")+ scale_fill_manual(values=c("#373332","#736F6E" ))+scale_x_discrete(limits=Limits)

}



df2ed_multiple_experiments<-function(data_ostrich,data_fcfs,assoc){



associ=assoc

	shortlong=function(i){
		if (i==1)
			return("Long")
		if (i==0)
			return("Short")
	}
m=64
Limits=c("Short","Long")

for (i in 1:40){
	Co<-campaign_detection_ed(data_ostrich[[i]])
	Cf<-campaign_detection_ed(data_fcfs[[i]])
	assoc=read.table(associ[[i]])
	names(assoc)=c("user","category")
	
	Uo=max_stretches(Co,m)
	Uo$category=lapply(assoc[Uo$user,]$category,shortlong)
	Uf=max_stretches(Cf,m)
	Uf$category=lapply(assoc[Uf$user,]$category,shortlong)
	print(Uo)
	print(Uf)


	if (exists("U")){

	U=rbind(U,Uo,Uf)

	}else{
 U=rbind(Uo,Uf)

	}

 	}

	ostrich_max_mean_short=cbind("Ostrich","Short",ci(Uo[Uo$category=="Short",]$max_stretch))
	ostrich_max_mean_long=cbind("Ostrich","Long",ci(Uo[Uo$category=="Long",]$max_stretch))
	fcfs_max_mean_short=cbind("FCFS","Short",ci(Uf[Uf$category=="Short",]$max_stretch))
	fcfs_max_mean_long=cbind("FCFS","Long",ci(Uf[Uf$category=="Long",]$max_stretch))
	
	colnames(ostrich_max_mean_short)=c("Algorithm","category","n","max_stretch","sd","se","lowerci","upperci")
	colnames(ostrich_max_mean_long)=c("Algorithm","category","n","max_stretch","sd","se","lowerci","upperci")
	colnames(fcfs_max_mean_short)=c("Algorithm","category","n","max_stretch","sd","se","lowerci","upperci")
	colnames(fcfs_max_mean_long)=c("Algorithm","category","n","max_stretch","sd","se","lowerci","upperci")

	U=rbind(ostrich_max_mean_short,ostrich_max_mean_long,fcfs_max_mean_short, fcfs_max_mean_long)

	gobj=	ggplot(U, aes(x=category, y=max_stretch, fill=Algorithm)) + 
    geom_bar(position=position_dodge(), stat="identity") +
    ylab("Max Stretch Mean, 95% confidence interval")+xlab("User Job length profile")+ scale_fill_manual(values=c("#373332","#736F6E" ))+scale_x_discrete(limits=Limits)+scale_y_log10()
	gobj
    	print(ggplot_build(gobj))

}



