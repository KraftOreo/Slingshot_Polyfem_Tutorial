//cube([4.85,0.1,210],center=true,$fn=10000,$fs=0.01);
for(i=[-105:1:105]){
    for(j=[-2.43:0.2:2.43]){
       translate([j,0,i])
        cube([0.2,0.1,1],center=true);
    }
}

