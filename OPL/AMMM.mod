int nServices=...;
int nDrivers=...;
int nBuses=...;
int maxBuses=...;
float CBM=...;
float CEM=...;
int BM=...;

range S=1..nServices;
range B=1..nBuses;
range D=1..nDrivers;

int ST[s in S]=...;
int DM[s in S]=...;
int DK[s in S]=...;
int NP[s in S]=...;
int OV[s1 in S, s2 in S];

int cap[b in B]=...;
float eurosMin[b in B]=...;
float eurosKm[b in B]=...;

int maxD[d in D]=...;

dvar boolean BS[b in B, s in S];
dvar boolean DS[d in D, s in S];
dvar int worked[d in D];
dvar boolean usedB[b in B];
dvar boolean extra[d in D]; //True iff the driver d works extra time

//Calculate overlapping between services
execute{
	
	var s1;
	var s2;
	for(s1 in S){
		for(s2 in S){
			if(s1 != s2 & OV[s1][s2]!=1){
				if((ST[s1] <= ST[s2] && ST[s2] <= ST[s1]+DM[s1]) || (ST[s2] <= ST[s1] && ST[s1] <= ST[s2]+DM[s2])){
					OV[s1][s2]=1;
					OV[s2][s1]=1;
	 			}			
			}		
		}		
	}
	cplex.tilim = 3600
	cplex.epagap <= 0.01
}
  
// Objective
minimize sum(d in D)(worked[d]*CBM + (worked[d]-BM)*(CEM-CBM)*extra[d]) + sum(b in B)sum(s in S)(eurosMin[b]*DM[s]*BS[b][s] + eurosKm[b]*DK[s]*BS[b][s]);

subject to{
	//if(worked - BM < 0) -> extra = 0
	forall(d in D) BM-worked[d] <= (1-extra[d])*BM;
	//if(worked - BM > 0) -> extra = 1
	forall(d in D) worked[d] - BM <= extra[d]*maxD[d];
		
	//Maximum amount of time a driver can work
	forall(d in D) worked[d] <= maxD[d];
	//Worked time = sum of all services
	forall(d in D) sum(s in S) DS[d][s]*DM[s] == worked[d];
	
	//Needed capacity
	forall(s in S) sum(b in B) BS[b][s]*cap[b] >= NP[s];
	
	//One driver can't be assigned to two services that are overlapped
	forall(d in D) forall(s1,s2 in S:s1!=s2 && OV[s1][s2]==1) DS[d][s1] + DS[d][s2] <= 1;
	
	//One bus can't be assigned to two services that are overlapped
	forall(b in B) forall(s1,s2 in S:s1!=s2 && OV[s1][s2]==1) BS[b][s1] + BS[b][s2] <= 1;
	
	//Num of drivers equal to num of buses
	forall(s in S) sum(d in D)DS[d][s] == sum(b in B)BS[b][s];
	
	//MaxBuses
	sum(b in B)usedB[b] <= maxBuses;
	
	//sum(buses)>0 -> used = 1
	forall(b in B) sum(s in S)BS[b][s] <= usedB[b]*(nServices+1);
	//sum(buses) = 0 -> used = 0
	forall(b in B) usedB[b] <= sum(s in S)BS[b][s]*(nServices+1);
}

//Checking solutions
execute{
	var d, b, s1, s2, error;
	error = false;
	
	//Driver overlapping
	for(d in D)
		for(s1 in DS[d])
			if(DS[d][s1]== 1)
				for(s2 in DS[d])
					if(DS[d][s2]== 1)	
						if(OV[s1][s2]== 1 && s1 < s2){
							writeln("ERROR: Driver " + d + " is working on " + s1 + " and " + s2 + " at the same time.");
							error = true;
    					}						
	if(error)
		writeln("Driver overlapping test FAILED.");
	else
		writeln("Driver overlapping test SUCCEED.");
	
	//Bus overlapping
	for(b in B)
		for(s1 in BS[b])
			if(BS[b][s1]== 1)
				for(s2 in BS[b])
					if(BS[b][s2]== 1)	
						if(OV[s1][s2]== 1 && s1 < s2){
							writeln("ERROR: Bus " + b + " is used on " + s1 + " and " + s2 + " at the same time.");
							error = true;
    					}						
	if(error)
		writeln("Bus overlapping test FAILED.");
	else
		writeln("Bus overlapping test SUCCEED.");
		
	//Capacity
	var totalCap, s;
	error = false;
	for(s in S)
		totalCap = 0;
		for(b in B)
			if(BS[b][s])
				totalCap += cap[b]
		if (totalCap < NP[s])
			writeln("ERROR: Service " + s + " needs " + NP[s] + ", however buses capacity is " + totalCap);
	if(error)
		writeln("Service capacity test FAILED.");
	else
		writeln("Service capacity test SUCCEED.");							
	
	//MaxBuses
	var totalBuses;
	totalBuses = 0;
	for(b in B)
		if(usedB[b] == true)
			totalBuses+= 1
	if(totalBuses > maxBuses){
		writeln("ERROR: Total used buses " + totalBuses + " while maxBuses is " + maxBuses);
		writeln("MaxBuses test FAILED.");
	}
	else
		writeln("MaxBuses test SUCCEED.");
	
	//Same number of buses than drivers
	var totalDrivers;
	totalDrivers = 0;
	totalBuses = 0;
	for(s in S)
		for (b in B)
			if(BS[b][s]==true)
				totalBuses += 1;
		for (d in D)
			if(DS[d][s]==true)
				totalDrivers += 1;
	if(totalDrivers != totalBuses){
		writeln("ERROR: Total used buses " + totalBuses + " while total drivers is " + totalDrivers);
		writeln("One driver per bus test FAILED.");
	}
	else
		writeln("One driver per bus test SUCCEED.");
}

