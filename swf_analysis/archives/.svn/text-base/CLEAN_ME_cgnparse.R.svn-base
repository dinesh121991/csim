#cgn parser.
# TODO: finish it.
cgn2list<-function(filename){
	fh <- file( filename, open='rt' )
	L<-list(readLines(fh,6))
	lines <- readLines(fh)
	lines=lapply(lines,strsplit,":")
	D=list()
	for (i in 1:length(lines)){
		tmp=lines[[i]][[1]][1]
		D$`tmp`=lines[[i]][[1]][2]	
	}
	tmp=trsplit(lines, ":")
	L$line[1]=line[2]
	tmp <- strsplit(line, "\\t")
	first <- tmp[[1]][1]; second <- tmp[[1]][2]; third <- tmp[[1]][3]
	print(first)


}
