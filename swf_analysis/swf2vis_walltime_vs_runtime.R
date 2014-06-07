#!/usr/bin/Rscript


################WORKING DIRECTORY MAGIC##########
##################DO NOT ALTER###################
initial.options <- commandArgs(trailingOnly = FALSE)
file.arg.name <- "--file="
script.name <- sub(file.arg.name, "", initial.options[grep(file.arg.name, initial.options)])
script.basename <- dirname(script.name)
execution_wd=getwd()
setwd(script.basename)
base_script_wd=getwd()
###################END BLOCK#####################

##############COMMON REQUIREMENTS################
##################DO NOT ALTER###################
#Parser file with all the parser types.
source('Rscript/parser.R')
###################END BLOCK#####################


##############SCRIPT PARAMETERS##################
#############MODIFY AS REQUIRED##################

#Path file for setting up the location of your R files.
#you can alternatively set rfold='/path/to/your/files', but its less modular.
source('Rscript/path.R')

#description and epilog for the console help output.
#e.g. description="This scripts does this and that."
#e.g. epilog="use with caution. refer to www.site.com .."
description='This tool will plot system utilization for the whole log file.'
epilog='You can input multiple swf files, they will be cat.'


#External parser function: for usual options.
#e.g. parser=parser_swf(description,epilog)
parser=parser_swf_minimal(description,epilog)


#additional argparse entries for this particular script.
#e.g. parser$add_argument('-s','--sum', dest='accumulate', action='store_const', const=sum, default=max,help='sum the integers (default: find the max)')

#files you want to source from the rfold folder for this Rscript
#e.g. c('common.R','histogram.R')
userfiles=c('common.R',"analysis.R","visu.R")
###################END BLOCK#####################


###SOURCING, CONTEXT CLEANING, ARG RETRIEVE######
##################DO NOT ALTER###################
#code insertion.
rm(list=setdiff(ls(),c("parser","rfold","userfiles","execution_wd","base_script_wd")))
args=parser$parse_args()
#Verbosity management.
source('Rscript/verbosity.R')
verb<-verbosity_function_maker(args$verbosity)
verb(args,"Parameters to the script")

setwd(rfold)
rfold_wd=getwd()
for (filename in userfiles) {
  source(filename)
}


setwd(base_script_wd)
rm(parser,rfold,userfiles)
###################END BLOCK#####################


#####################OUTPUT_MANAGEMENT###########
################MODIFY IF NEEDED####################
source('Rscript/output_management.R')
options_vector=set_output(args$device,args$output,args$ratio,execution_wd)
###################END BLOCK#####################


#############BEGIN YOUR RSCRIPT HERE.############
#here is your working directory :)
setwd(execution_wd)
#You have access to:
#set_output(device='pdf',filename='tmp.pdf',ratio=1)
#use it if you really want to change the output type on your way.
#pause_output(pause=TRUE) for x11
#use it to pause for output.
#args for retrieving your arguments.


#type stuff here.
data=swf_read(args$swf_filenames[1])
#print(data)
#graph_reqtime_vs_runtime(data)

graph_reqtime_vs_runtime_marginal_distributions_compared(data)+xlab("Value")+ylab("Job Count")
#graph_reqtime_vs_runtime_marginal_distributions_compared(data,by=1000,high_treshold=12500)
#graph_reqtime_vs_runtime_marginal_distributions_compared(data,by=100,high_treshold=12500)
#graph_reqtime_vs_runtime_marginal_distributions_compared(data,by=10,high_treshold=12500)
#graph_reqtime_vs_runtime_marginal_distributions_compared(data,by=100,high_treshold=1250)
#graph_reqtime_vs_runtime_marginal_distributions_compared(data,by=10,high_treshold=125)
#graph_reqtime_vs_runtime_marginal_distributions_compare_densities(data)
#graph_reqtime_vs_runtime_marginal_distributions_compare_densities(data,high_treshold=12500)
#graph_reqtime_vs_runtime_marginal_distributions_compare_densities(data,high_treshold=12500)
#graph_reqtime_vs_runtime_marginal_distributions_compare_densities(data,high_treshold=12500)
#graph_reqtime_vs_runtime_marginal_distributions_compare_densities(data,high_treshold=1250)
#graph_reqtime_vs_runtime_marginal_distributions_compare_densities(data,high_treshold=125)
graph_reqtime_vs_runtime_ratio_histogram(data)+xlab("Runtime/Reqtime value")+ylab("Job Count")
#graph_reqtime_vs_runtime_ratio_density(data)
#graph_reqtime_vs_runtime_ratio_histogram(data,runtime_low_treshold=60)
#graph_reqtime_vs_runtime_ratio_histogram(data,runtime_high_treshold=80000,runtime_low_treshold=60)
#graph_reqtime_vs_runtime_ratio_per_user(data)
#graph_reqtime_vs_runtime_expzoom_ratio_histogram(data,by=0.01)
#graph_reqtime_vs_runtime_heatmap(data,binwidth=c(100, 100),xlimits=c(0,100000),ylimits=c(0,100000))
#graph_reqtime_vs_runtime_heatmap(data,binwidth=c(1000, 1000),xlimits=c(0,200000),ylimits=c(0,200000))
#graph_reqtime_vs_runtime_heatmap(data,binwidth=c(7000, 7000),xlimits=c(0,200000),ylimits=c(0,200000))
#graph_reqtime_vs_runtime_heatmap_log10scale(data,binwidth=c(0.3, 0.3),xlimits=c(0,6),ylimits=c(0,6))
#graph_reqtime_vs_runtime_heatmap_log10scale(data,binwidth=c(0.1, 0.1),xlimits=c(0,6),ylimits=c(0,6))
#graph_cores_vs_runtime_heatmap(data,binwidth=c(3000, 300),xlimits=c(+1,80000),ylimits=c(+1,12000))
#graph_cores_vs_runtime_heatmap(data,binwidth=c(100, 300),xlimits=c(+1,2000),ylimits=c(+1,12000))
#graph_cores_vs_runtime_heatmap(data,binwidth=c(10, 300),xlimits=c(+1,200),ylimits=c(+1,12000))
#graph_cores_vs_runtime_heatmap(data,binwidth=c(10, 300),xlimits=c(+1,200),ylimits=c(+1,12000))
#graph_cores_vs_runtime_heatmap(data,binwidth=c(100, 5),xlimits=c(-1,2000),ylimits=c(-1,120))

pause_output(options_vector)


###################END BLOCK#####################


#############X11 OUTPUT MANAGEMENT###############
#################MODIFY IF NEEDED################
#pause_output(options_vector)
###################END BLOCK#####################


