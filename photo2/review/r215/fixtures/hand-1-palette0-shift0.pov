#version 3.7;
global_settings {assumed_gamma 1}
camera {orthographic location <0,-40,65> look_at <0,0,8> right x*72 up y*72}
#declare nbeads=312;
#declare beads_per_row=6.5;
#declare rclock=0;
#declare nrows = floor(0.5 + (nbeads / beads_per_row));  
#declare exact_beads_per_row = nbeads / nrows;  

#declare chain_minor = 4;
#declare bead_radius = chain_minor * 0.96 * sin(180 / beads_per_row);
#declare maximum_height_per_bead_size = 0.65;
#declare bead_maximum_height = maximum_height_per_bead_size * (2 * bead_radius);
#declare chain_major = bead_maximum_height * 1.05 * nrows / (2 * pi);


#declare hole_size_per_bead_size=.14;
#macro bead(bead_material, roundedness, height_per_bead_size, bead_relative_size)
#local bead_actual_radius = bead_radius * bead_relative_size;
#local bead_major = bead_actual_radius * 0.5 * ( 1 + hole_size_per_bead_size );
#local bead_minor = bead_actual_radius - bead_major;
#local hole_radius = bead_major - bead_minor;

#local bead_round = roundedness * bead_minor;
#local bead_extra_half_width  = bead_minor - bead_round;
#local bead_total_half_width  = bead_minor;

#local bead_desired_half_height = height_per_bead_size * bead_actual_radius;
#local bead_height_scaling = bead_desired_half_height / bead_minor;
#local bead_extra_half_height = bead_height_scaling * bead_extra_half_width;
#local bead_total_half_height = bead_desired_half_height;

merge {
  // short wide
  difference { cylinder { <0, -bead_extra_half_height, 0>, <0, bead_extra_half_height, 0>, 
                          bead_major+bead_total_half_width }
               cylinder { <0, -bead_extra_half_height * 1.0001, 0>, <0, bead_extra_half_height * 1.0001, 0>, 
                          bead_major-bead_total_half_width } }
  // tall narrow
  difference { cylinder { <0, -bead_total_half_height, 0>, <0, bead_total_half_height, 0>, 
                          bead_major+bead_extra_half_width }
               cylinder { <0, -bead_total_half_height * 1.0001, 0>, <0, bead_total_half_height * 1.0001, 0>, 
                          bead_major-bead_extra_half_width } }
  // outer
  torus {bead_major+bead_extra_half_width bead_round 
         scale <1.0, bead_height_scaling, 1.0> translate <0, bead_extra_half_height, 0>}
  torus {bead_major+bead_extra_half_width bead_round 
         scale <1.0, bead_height_scaling, 1.0> translate <0, -bead_extra_half_height, 0>}
  // inner
  torus {bead_major-bead_extra_half_width bead_round 
         scale <1.0, bead_height_scaling, 1.0> translate <0, bead_extra_half_height, 0>}
  torus {bead_major-bead_extra_half_width bead_round 
         scale <1.0, bead_height_scaling, 1.0> translate <0, -bead_extra_half_height, 0>}
  material { bead_material } }
#end

light_source {<0,-100,120> rgb 1.6}
plane {z,0 pigment{rgb <0.52,0.43,0.34>} finish{ambient .25 diffuse .7}}
#declare m0=material{texture{pigment{rgb <0.02,0.18,0.8>} finish{ambient .08 diffuse .7 phong 1.4 phong_size 45}}};
#declare b0=bead(m0,.8,.7,1);
#declare m1=material{texture{pigment{rgb <0.95,0.48,0.015>} finish{ambient .08 diffuse .7 phong 1.4 phong_size 45}}};
#declare b1=bead(m1,.8,.7,1);
#declare m2=material{texture{pigment{rgb <0.009,0.009,0.009>} finish{ambient .08 diffuse .7 phong 1.4 phong_size 45}}};
#declare b2=bead(m2,.8,.7,1);
#declare bead_index=0;
#while(bead_index<nbeads)
  #declare chain_angle = 360*(bead_index/nbeads + rclock*0.1666);
  #declare row_angle = -360*(bead_index/exact_beads_per_row + rclock*1.00);
  #declare t1 = vaxis_rotate(<chain_major, 0, 0>, z, chain_angle);
  #declare t2 = vaxis_rotate(<0, 0, chain_minor>, vcross(-z, t1), row_angle); 
#switch(mod(bead_index,3))
#case(0) object{b0 rotate z*chain_angle translate t1+t2+<0,0,chain_minor+2*bead_radius> translate <0,0,0>} #break
#case(1) object{b1 rotate z*chain_angle translate t1+t2+<0,0,chain_minor+2*bead_radius> translate <0,0,0>} #break
#case(2) object{b2 rotate z*chain_angle translate t1+t2+<0,0,chain_minor+2*bead_radius> translate <0,0,0>} #break
#end
#declare bead_index=bead_index+1;
#end
