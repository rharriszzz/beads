/* copyright 2003 Richard Harris */

#include "colors.inc" 

/* +KFF2400 +fj +Omovie */
/* +KFF7 +fj +Obeads */

camera {
    location <50, -600, 500>
    look_at 0
    angle 10 }
    
light_source { <100, -1000, 1000> White*1.4 }
plane { z, 0 pigment { White } finish { diffuse 0.90 }}

/* begin settings */      
#declare bclock = clock * 0.99999;
#declare bead_pattern_count = 8;
#declare bead_pattern = 1+floor(bclock*bead_pattern_count);
#declare rclock = bclock*bead_pattern_count - floor(bclock*bead_pattern_count);
/* end settings */

#switch (bead_pattern)

#case (1)
#declare color_pattern = array[24]{
0, 1, 1, 1, 1, 2,
0, 0, 1, 1, 1, 2, 
0, 0, 0, 1, 1, 2,
0, 0, 0, 0, 1, 2};
#declare pattern_rows_per_group = 4;
#declare beads_per_row = 6.5;
#declare ngroups = 28;
#break

#case (2)
#declare color_pattern = array[35]{
0,1,1,2,3,2,1,
0,1,2,3,3,2,1,
0,1,2,3,2,1,1,
0,1,2,2,1,2,1,
0,1,2,1,2,2,1}; 
#declare pattern_rows_per_group = 5; 
#declare beads_per_row = 6.5;
#declare ngroups = 20;
#break

#case (3)
#declare n1 = 50;
#declare n2 = 12;
#declare color_pattern = array[(n1+n2)*6];
#declare index = 0;
#while (index < n1)
  #declare color_pattern[3*index+0] = 0;
  #declare color_pattern[3*index+1] = 1;
  #declare color_pattern[3*index+2] = 1;
  #declare color_pattern[3*(index+n1+n2)+0] = 1;
  #declare color_pattern[3*(index+n1+n2)+1] = 0;
  #declare color_pattern[3*(index+n1+n2)+2] = 0;
  #declare index = index + 1;
#end
#declare index = 0;
#while (index < n2)
  #declare color_pattern[3*(index+n1)+0] = 2;
  #declare color_pattern[3*(index+n1)+1] = 2;
  #declare color_pattern[3*(index+n1)+2] = 2;
  #declare color_pattern[3*(index+n1+n2+n1)+0] = 2;
  #declare color_pattern[3*(index+n1+n2+n1)+1] = 2;
  #declare color_pattern[3*(index+n1+n2+n1)+2] = 2;
  #declare index = index + 1;
#end
#declare beads_per_row = 6.5;
#declare ngroups = 2;
#break

#case (4)
#declare color_pattern = array[42]{
0,1,1,2,2,3,3,
 0,1,4,2,4,3,4,
  0,3,3,1,1,2,2,
   0,3,4,1,4,2,4,
    0,2,2,3,3,1,1,
     0,2,4,3,4,1,4};
#declare pattern_rows_per_group = 6;
#declare beads_per_row = 6.5;
#declare ngroups = 18;
#break

#case (5)
#declare color_pattern = array[42]{
3,2,1,0,1,2,3,
 2,1,0,0,1,2,
2,1,0,1,0,1,2,
 1,0,1,1,0,1,
1,0,1,2,1,0,1,
 0,1,2,2,1,0,   
0,1,2};
#declare pattern_rows_per_group = 6;
#declare beads_per_row = 6.5;
#declare ngroups = 18;
#break  

#case (6)
#declare color_pattern = array[84]{
2,1,3,0,3,1,2,
 1,3,0,0,3,1,
1,3,0,3,0,3,1,
 3,0,3,3,0,3,
3,0,3,2,3,0,3,
 0,3,2,2,3,0,   
0,3,2,1,2,3,0,
 3,2,1,2,3,0,
0,3,2,2,3,0,3,
 0,3,2,3,0,3, 
3,0,3,3,0,3,1,
 3,0,3,0,3,1,
1,3,0,0,3,1};
#declare pattern_rows_per_group = 6;
#declare beads_per_row = 6.5;
#declare ngroups = 9;
#break
 
#case (7)
#declare color_pattern = array[24]{
0,1,2,2,2,2,
0,1,1,2,2,2,
0,1,1,1,2,2,
0,1,1,1,1,2};             
#declare pattern_rows_per_group = 4;
#declare beads_per_row = 6.5;
#declare ngroups = 28;
#break 
 
#case (8)
#declare color_pattern = array[30]{
0,0,1,1,3,3,
0,0,2,2,3,3,
3,3,2,2,0,0,
3,3,1,1,0,0,
4,4,4,4,4,4};
#declare pattern_rows_per_group = 5;
#declare beads_per_row = 6.5;
#declare ngroups = 24;
#break 
 
#end

#declare pattern_length = dimension_size(color_pattern, 1);
#declare nbeads = ngroups * pattern_length;
#declare nrows = floor(0.5 + (nbeads / beads_per_row));  
#declare exact_beads_per_row = nbeads / nrows;  

#declare chain_minor = 4;
#declare bead_radius = chain_minor * 0.96 * sin(180 / beads_per_row);
#declare maximum_height_per_bead_size = 0.65;
#declare bead_maximum_height = maximum_height_per_bead_size * (2 * bead_radius);
#declare chain_major = bead_maximum_height * 1.05 * nrows / (2 * pi);

/* bead_major - bead_minor = hole_radius = bead_radius * hole_size_per_bead_size */
/* bead_major + bead_minor = bead_radius */
/* so, 2 * bead_major = bead_radius * (1 + hole_size_per_bead_size) */

#declare hole_size_per_bead_size = 0.14;

//#declare roundedness = 0.8; /* from 0.0 to less than 1.0 */
//#declare height_per_bead_size = 0.70; /* from 0.5 to 2.0 */
//#declare bead_relative_size = 1.00; /* from 0.5 to 1.0 */

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

#macro shiny_opaque(bead_color)
material{texture{pigment{bead_color} finish {phong 1.5}}}
#end

#macro frosted_opaque(bead_color)       
material{texture{pigment{bead_color} 
                 finish {diffuse 0.5 specular 0.35 conserve_energy}}}
#end
                    
#macro shiny_translucent(bead_color)
material{texture{pigment{bead_color filter 0.3} 
                 finish {diffuse 0.5 specular 0.75 conserve_energy}} 
                 interior{ior 1.5}}
#end
                    
#macro frosted_translucent(bead_color)
material{texture{pigment{bead_color filter 0.3} 
                 finish {diffuse 0.5 specular 0.35 conserve_energy}} 
                 interior{ior 1.5}}
#end

#switch (bead_pattern)

#case (1)
#declare beads = array[3];
#declare beads[0] = bead(shiny_opaque(Red),   0.8, 0.7, 1.0);
#declare beads[1] = bead(shiny_opaque(Green), 0.8, 0.7, 1.0);
#declare beads[2] = bead(shiny_opaque(Blue),  0.8, 0.7, 1.0);
#break

#case (2)
#declare MyBlue = color rgb <0.20, 0, 0.75>;
#declare beads = array[4];
#declare beads[0] = bead(shiny_opaque(MyBlue),           0.85, 0.65, 1.0);
#declare beads[1] = bead(frosted_translucent(Plum),      0.7, 0.7, 1.0);
#declare beads[2] = bead(frosted_translucent(OrangeRed), 0.7, 0.7, 1.0);
#declare beads[3] = bead(frosted_translucent(Yellow),    0.7, 0.7, 1.0);
#break

#case (3)
#declare beads = array[3];
#declare beads[0] = bead(shiny_opaque(White), 0.8, 0.7, 1.0);
#declare beads[1] = bead(shiny_opaque(Black), 0.8, 0.7, 1.0);
#declare beads[2] = bead(shiny_opaque(Red),   0.8, 0.7, 1.0);
#break

#case (4)
#declare beads = array[5];
#declare beads[0] = bead(frosted_translucent(Red),    0.64, 0.7, 1.0);
#declare beads[1] = bead(frosted_translucent(Yellow), 0.64, 0.7, 1.0);
#declare beads[2] = bead(frosted_translucent(Green),  0.64, 0.7, 1.0);
#declare beads[3] = bead(frosted_translucent(SlateBlue),   0.64, 0.7, 1.0);
#declare beads[4] = bead(shiny_opaque(White),         0.64, 0.7, 1.0);
#break

#case (5)              
#declare Dark_Purple = color red 0.38 green 0.12 blue 0.37;
#declare Med_Purple =  color red 0.73 green 0.16 blue 0.96;
#declare Light_Purple = color red 0.87 green 0.58 blue 0.98;
#declare beads = array[6];
#declare beads[0] = bead(frosted_opaque(Black),  0.8, 0.7, 1.0);
#declare beads[1] = bead(shiny_translucent(Dark_Purple), 0.8, 0.7, 1.0);
#declare beads[2] = bead(shiny_translucent(Light_Purple),   0.8, 0.7, 1.0);
#declare beads[3] = bead(shiny_translucent(White),  0.8, 0.7, 1.0); 
#break  

#case (6)              
#declare Dark_Purple = color red 0.38 green 0.12 blue 0.37;
#declare Med_Purple =  color red 0.73 green 0.16 blue 0.96;
#declare Light_Purple = color red 0.87 green 0.58 blue 0.98;
#declare beads = array[4];
#declare beads[0] = bead(shiny_translucent(White),  0.8, 0.7, 1.0);
#declare beads[1] = bead(shiny_translucent(Dark_Purple), 0.8, 0.7, 1.0);
#declare beads[2] = bead(shiny_translucent(Light_Purple),   0.8, 0.7, 1.0);
#declare beads[3] = bead(frosted_opaque(Gray20),  0.8, 0.7, 1.0);
#break 

#case (7)
#declare beads = array[3];
#declare beads[0] = bead(shiny_opaque(White),   0.8, 0.7, 1.0);
#declare beads[1] = bead(shiny_opaque(Red), 0.8, 0.7, 1.0);
#declare beads[2] = bead(shiny_opaque(SteelBlue),  0.8, 0.7, 1.0);
#break

#case (8)
#declare beads = array[5];
#declare beads[0] = bead(shiny_translucent(White),  0.8, 0.7, 1.0);
#declare beads[1] = bead(shiny_translucent(Red), 0.8, 0.7, 1.0);
#declare beads[2] = bead(shiny_translucent(LightBlue),   0.8, 0.7, 1.0);
#declare beads[3] = bead(shiny_translucent(LimeGreen),  0.8, 0.7, 1.0); 
#declare beads[4] = bead(shiny_translucent(Black),  0.8, 0.7, 1.0);
#break

#end

#declare bead_index = 0;
#while ( bead_index < nbeads )   
  #declare chain_angle = 360*(bead_index/nbeads + rclock*0.1666);
  #declare row_angle = 360*(bead_index/exact_beads_per_row + rclock*1.00);
  #declare t1 = vaxis_rotate(<chain_major, 0, 0>, z, chain_angle);
  #declare t2 = vaxis_rotate(<0, 0, chain_minor>, vcross(-z, t1), row_angle); 
  object{ beads[color_pattern[mod(bead_index, pattern_length)]]
          rotate <0, 0, chain_angle>
          translate t1+t2+<0,0,chain_minor+2*bead_radius> }
  #declare bead_index = bead_index + 1;
#end