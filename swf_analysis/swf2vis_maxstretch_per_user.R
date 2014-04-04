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
description='Displays campaign stretches for all users, as a barplot.'
epilog='You may input as many swf files as you wish.'

#External parser function: for usual options.
#e.g. parser=parser_swf(description,epilog)
parser=parser_swf_with_cores(description,epilog)

#additional argparse entries for this particular script.
#e.g. parser$add_argument('-s','--sum', dest='accumulate', action='store_const', const=sum, default=max,help='sum the integers (default: find the max)')

#files you want to source from the rfold folder for this Rscript
#e.g. c('common.R','histogram.R')
userfiles=c('campaign_analysis.R','campaign_scheduling_metrics.R','campaign_detection.R','utilization.R')

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

#This function outputs a dataframe with users,max_stretch columns.
#the arguments shoulde be a vector with swf filename and number of cores.
produce_user_max_stretches_data  <- function(dfargs) {
    #Remove This
    verb(dfargs,d="dfargs")
    #--end rem
	verb("entered produce_user_max_stretches_data")
	swf_filename=dfargs[1]
	cores=dfargs[2]
	verb(swf_filename,cores)

	data<-swf_read(swf_filename)	
	C<-swf_campaign_detection(data)
	if(cores==0){
		cores=max_cores(data)
	}
	C<-add_stretch_column(C,cores=cores)

	U<-max_stretches(C)
    #Remove this:
    verb(C,d="Data ready to plot:")
    #--end Remove this
	colnames(U)=c("user","stretch")
	return(U)

    verb(data_ready_to_plot,d="Data ready to plot:")
}

if ( is.null(args$cores) ) {
	cores=rep(0,length(args$swf_filenames))
	verb(cores,d="Calculating all cores with utilization()")
}

arguments=(cbind(args$swf_filenames,cores))
data_ready_to_plot=apply(arguments,1,produce_user_max_stretches_data)

verb(data_ready_to_plot,d="Data ready to plot:")

if (length(args$labels)==1){
	if (args$labels=='') {
		args$labels=FALSE
	}
}
if (args$labelstitle==''){
	args$labelstitle="Log ID"
}
plot_user_individual_stretches(data_ready_to_plot,ylabel="Max Stretch",bw=args$grey,labelnames=args$labels,labelstitle=args$labelstitle)

###################END BLOCK#####################


#############X11 OUTPUT MANAGEMENT###############
#################MODIFY IF NEEDED################
pause_output(options_vector)
###################END BLOCK#####################


