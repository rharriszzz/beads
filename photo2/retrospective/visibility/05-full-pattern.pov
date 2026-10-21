#version 3.7;
global_settings {assumed_gamma 1 max_trace_level 12 ambient_light rgb 1}
background {color rgb 1}
camera {orthographic location <0,0,200> direction <0,0,-1>
 right x*34 up y*49}
light_source {<-50,170,250> color rgb .85 parallel point_at <0,0,0>}
light_source {<120,20,180> color rgb .35 parallel point_at <0,0,0> shadowless}
#declare bead_radius=.95;
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


#declare BeadR=bead(material{texture{
 pigment{color rgb <0.66000000,0.02500000,0.04500000>} finish{ambient .20 diffuse .72 specular .13 roughness .055}
}},.8,.55,1);
#declare BeadY=bead(material{texture{
 pigment{color rgb <1.00000000,0.65000000,0.02500000>} finish{ambient .20 diffuse .72 specular .13 roughness .055}
}},.8,.55,1);
#declare BeadB=bead(material{texture{
 pigment{color rgb <0.01800000,0.02500000,0.03500000>} finish{ambient .20 diffuse .72 specular .13 roughness .055}
}},.8,.55,1);
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "THE COMPLETE 208-POSITION CANDIDATE" .002,0 scale 0.72 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0,22.8,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "Alternating 6 / 7 rows; positions 0-207 each shown once" .002,0 scale 0.43 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0,21.4,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "201 supported colors; 7 outlined provisional blacks" .002,0 scale 0.45 texture {pigment {color rgb <0.00200000,0.16000000,0.19000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0,20.3,10>}
box{<-12.7,-18.9,-5>,<12.7,19,-4.99> texture {pigment {color rgb <0.96800000,0.97600000,0.98000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-7.5,18.0,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-7.5,18.0,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "0" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-7.5,17.85,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-4.5,18.0,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-4.5,18.0,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "1" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-4.5,17.85,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-1.5,18.0,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-1.5,18.0,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "2" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-1.5,17.85,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <1.5,18.0,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <1.5,18.0,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "3" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <1.5,17.85,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <4.5,18.0,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <4.5,18.0,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "4" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <4.5,17.85,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <7.5,18.0,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <7.5,18.0,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "5" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <7.5,17.85,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-9.0,16.85,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-9.0,16.85,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "6" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-9.0,16.700000000000003,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-6.0,16.85,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-6.0,16.85,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "7" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-6.0,16.700000000000003,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-3.0,16.85,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-3.0,16.85,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "8" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-3.0,16.700000000000003,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <0.0,16.85,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <0.0,16.85,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "9" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0.0,16.700000000000003,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <3.0,16.85,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <3.0,16.85,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "10" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <3.0,16.700000000000003,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <6.0,16.85,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <6.0,16.85,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "11" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <6.0,16.700000000000003,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <9.0,16.85,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <9.0,16.85,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "12" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <9.0,16.700000000000003,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-7.5,15.7,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-7.5,15.7,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "13" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-7.5,15.549999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-4.5,15.7,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-4.5,15.7,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "14" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-4.5,15.549999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-1.5,15.7,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-1.5,15.7,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "15" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-1.5,15.549999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <1.5,15.7,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <1.5,15.7,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "16" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <1.5,15.549999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <4.5,15.7,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <4.5,15.7,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "17" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <4.5,15.549999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <7.5,15.7,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <7.5,15.7,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "18" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <7.5,15.549999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-9.0,14.55,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-9.0,14.55,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "19" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-9.0,14.4,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-6.0,14.55,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-6.0,14.55,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "20" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-6.0,14.4,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-3.0,14.55,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-3.0,14.55,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "21" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-3.0,14.4,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <0.0,14.55,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <0.0,14.55,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "22" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0.0,14.4,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <3.0,14.55,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <3.0,14.55,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "23" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <3.0,14.4,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <6.0,14.55,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <6.0,14.55,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "24" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <6.0,14.4,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <9.0,14.55,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <9.0,14.55,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "25" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <9.0,14.4,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-7.5,13.4,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-7.5,13.4,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "26" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-7.5,13.25,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-4.5,13.4,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-4.5,13.4,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "27" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-4.5,13.25,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-1.5,13.4,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-1.5,13.4,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "28" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-1.5,13.25,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <1.5,13.4,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <1.5,13.4,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "29" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <1.5,13.25,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <4.5,13.4,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <4.5,13.4,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "30" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <4.5,13.25,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <7.5,13.4,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <7.5,13.4,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "31" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <7.5,13.25,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-9.0,12.25,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-9.0,12.25,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "32" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-9.0,12.1,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-6.0,12.25,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-6.0,12.25,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "33" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-6.0,12.1,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-3.0,12.25,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-3.0,12.25,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "34" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-3.0,12.1,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <0.0,12.25,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <0.0,12.25,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "35" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0.0,12.1,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <3.0,12.25,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <3.0,12.25,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "36" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <3.0,12.1,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <6.0,12.25,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <6.0,12.25,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "37" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <6.0,12.1,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <9.0,12.25,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <9.0,12.25,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "38" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <9.0,12.1,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-7.5,11.100000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-7.5,11.100000000000001,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "39" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-7.5,10.950000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-4.5,11.100000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-4.5,11.100000000000001,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "40" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-4.5,10.950000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-1.5,11.100000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-1.5,11.100000000000001,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "41" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-1.5,10.950000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <1.5,11.100000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <1.5,11.100000000000001,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "42" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <1.5,10.950000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <4.5,11.100000000000001,4> texture {pigment {color rgb <0.01500000,0.10000000,0.34000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <4.5,11.100000000000001,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "43" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <4.5,10.950000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <7.5,11.100000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <7.5,11.100000000000001,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "44" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <7.5,10.950000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-9.0,9.950000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-9.0,9.950000000000001,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "45" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-9.0,9.8,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-6.0,9.950000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-6.0,9.950000000000001,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "46" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-6.0,9.8,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-3.0,9.950000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-3.0,9.950000000000001,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "47" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-3.0,9.8,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <0.0,9.950000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <0.0,9.950000000000001,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "48" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0.0,9.8,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <3.0,9.950000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <3.0,9.950000000000001,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "49" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <3.0,9.8,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <6.0,9.950000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <6.0,9.950000000000001,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "50" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <6.0,9.8,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <9.0,9.950000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <9.0,9.950000000000001,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "51" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <9.0,9.8,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-7.5,8.8,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-7.5,8.8,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "52" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-7.5,8.65,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-4.5,8.8,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-4.5,8.8,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "53" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-4.5,8.65,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-1.5,8.8,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-1.5,8.8,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "54" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-1.5,8.65,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <1.5,8.8,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <1.5,8.8,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "55" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <1.5,8.65,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <4.5,8.8,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <4.5,8.8,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "56" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <4.5,8.65,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <7.5,8.8,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <7.5,8.8,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "57" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <7.5,8.65,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-9.0,7.65,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-9.0,7.65,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "58" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-9.0,7.5,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-6.0,7.65,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-6.0,7.65,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "59" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-6.0,7.5,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-3.0,7.65,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-3.0,7.65,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "60" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-3.0,7.5,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <0.0,7.65,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <0.0,7.65,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "61" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0.0,7.5,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <3.0,7.65,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <3.0,7.65,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "62" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <3.0,7.5,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <6.0,7.65,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <6.0,7.65,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "63" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <6.0,7.5,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <9.0,7.65,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <9.0,7.65,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "64" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <9.0,7.5,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-7.5,6.5,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-7.5,6.5,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "65" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-7.5,6.35,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-4.5,6.5,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-4.5,6.5,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "66" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-4.5,6.35,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-1.5,6.5,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-1.5,6.5,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "67" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-1.5,6.35,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <1.5,6.5,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <1.5,6.5,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "68" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <1.5,6.35,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <4.5,6.5,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <4.5,6.5,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "69" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <4.5,6.35,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <7.5,6.5,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <7.5,6.5,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "70" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <7.5,6.35,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-9.0,5.350000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-9.0,5.350000000000001,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "71" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-9.0,5.200000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-6.0,5.350000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-6.0,5.350000000000001,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "72" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-6.0,5.200000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-3.0,5.350000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-3.0,5.350000000000001,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "73" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-3.0,5.200000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <0.0,5.350000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <0.0,5.350000000000001,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "74" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0.0,5.200000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <3.0,5.350000000000001,4> texture {pigment {color rgb <0.01500000,0.10000000,0.34000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <3.0,5.350000000000001,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "75" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <3.0,5.200000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <6.0,5.350000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <6.0,5.350000000000001,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "76" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <6.0,5.200000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <9.0,5.350000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <9.0,5.350000000000001,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "77" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <9.0,5.200000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-7.5,4.200000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-7.5,4.200000000000001,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "78" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-7.5,4.050000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-4.5,4.200000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-4.5,4.200000000000001,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "79" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-4.5,4.050000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-1.5,4.200000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-1.5,4.200000000000001,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "80" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-1.5,4.050000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <1.5,4.200000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <1.5,4.200000000000001,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "81" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <1.5,4.050000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <4.5,4.200000000000001,4> texture {pigment {color rgb <0.01500000,0.10000000,0.34000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <4.5,4.200000000000001,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "82" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <4.5,4.050000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <7.5,4.200000000000001,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <7.5,4.200000000000001,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "83" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <7.5,4.050000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-9.0,3.0500000000000007,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-9.0,3.0500000000000007,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "84" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-9.0,2.900000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-6.0,3.0500000000000007,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-6.0,3.0500000000000007,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "85" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-6.0,2.900000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-3.0,3.0500000000000007,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-3.0,3.0500000000000007,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "86" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-3.0,2.900000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <0.0,3.0500000000000007,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <0.0,3.0500000000000007,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "87" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0.0,2.900000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <3.0,3.0500000000000007,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <3.0,3.0500000000000007,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "88" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <3.0,2.900000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <6.0,3.0500000000000007,4> texture {pigment {color rgb <0.01500000,0.10000000,0.34000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <6.0,3.0500000000000007,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "89" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <6.0,2.900000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <9.0,3.0500000000000007,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <9.0,3.0500000000000007,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "90" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <9.0,2.900000000000001,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-7.5,1.9000000000000021,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-7.5,1.9000000000000021,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "91" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-7.5,1.7500000000000022,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-4.5,1.9000000000000021,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-4.5,1.9000000000000021,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "92" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-4.5,1.7500000000000022,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-1.5,1.9000000000000021,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-1.5,1.9000000000000021,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "93" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-1.5,1.7500000000000022,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <1.5,1.9000000000000021,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <1.5,1.9000000000000021,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "94" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <1.5,1.7500000000000022,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <4.5,1.9000000000000021,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <4.5,1.9000000000000021,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "95" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <4.5,1.7500000000000022,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <7.5,1.9000000000000021,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <7.5,1.9000000000000021,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "96" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <7.5,1.7500000000000022,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-9.0,0.75,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-9.0,0.75,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "97" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-9.0,0.6,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-6.0,0.75,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-6.0,0.75,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "98" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-6.0,0.6,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-3.0,0.75,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-3.0,0.75,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "99" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-3.0,0.6,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <0.0,0.75,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <0.0,0.75,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "100" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0.0,0.6,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <3.0,0.75,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <3.0,0.75,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "101" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <3.0,0.6,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <6.0,0.75,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <6.0,0.75,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "102" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <6.0,0.6,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <9.0,0.75,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <9.0,0.75,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "103" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <9.0,0.6,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-7.5,-0.3999999999999986,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-7.5,-0.3999999999999986,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "104" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-7.5,-0.5499999999999986,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-4.5,-0.3999999999999986,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-4.5,-0.3999999999999986,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "105" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-4.5,-0.5499999999999986,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-1.5,-0.3999999999999986,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-1.5,-0.3999999999999986,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "106" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-1.5,-0.5499999999999986,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <1.5,-0.3999999999999986,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <1.5,-0.3999999999999986,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "107" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <1.5,-0.5499999999999986,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <4.5,-0.3999999999999986,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <4.5,-0.3999999999999986,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "108" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <4.5,-0.5499999999999986,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <7.5,-0.3999999999999986,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <7.5,-0.3999999999999986,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "109" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <7.5,-0.5499999999999986,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-9.0,-1.5499999999999972,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-9.0,-1.5499999999999972,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "110" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-9.0,-1.699999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-6.0,-1.5499999999999972,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-6.0,-1.5499999999999972,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "111" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-6.0,-1.699999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-3.0,-1.5499999999999972,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-3.0,-1.5499999999999972,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "112" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-3.0,-1.699999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <0.0,-1.5499999999999972,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <0.0,-1.5499999999999972,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "113" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0.0,-1.699999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <3.0,-1.5499999999999972,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <3.0,-1.5499999999999972,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "114" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <3.0,-1.699999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <6.0,-1.5499999999999972,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <6.0,-1.5499999999999972,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "115" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <6.0,-1.699999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <9.0,-1.5499999999999972,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <9.0,-1.5499999999999972,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "116" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <9.0,-1.699999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-7.5,-2.6999999999999993,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-7.5,-2.6999999999999993,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "117" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-7.5,-2.849999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-4.5,-2.6999999999999993,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-4.5,-2.6999999999999993,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "118" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-4.5,-2.849999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-1.5,-2.6999999999999993,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-1.5,-2.6999999999999993,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "119" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-1.5,-2.849999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <1.5,-2.6999999999999993,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <1.5,-2.6999999999999993,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "120" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <1.5,-2.849999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <4.5,-2.6999999999999993,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <4.5,-2.6999999999999993,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "121" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <4.5,-2.849999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <7.5,-2.6999999999999993,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <7.5,-2.6999999999999993,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "122" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <7.5,-2.849999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-9.0,-3.849999999999998,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-9.0,-3.849999999999998,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "123" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-9.0,-3.999999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-6.0,-3.849999999999998,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-6.0,-3.849999999999998,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "124" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-6.0,-3.999999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-3.0,-3.849999999999998,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-3.0,-3.849999999999998,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "125" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-3.0,-3.999999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <0.0,-3.849999999999998,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <0.0,-3.849999999999998,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "126" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0.0,-3.999999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <3.0,-3.849999999999998,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <3.0,-3.849999999999998,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "127" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <3.0,-3.999999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <6.0,-3.849999999999998,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <6.0,-3.849999999999998,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "128" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <6.0,-3.999999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <9.0,-3.849999999999998,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <9.0,-3.849999999999998,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "129" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <9.0,-3.999999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-7.5,-5.0,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-7.5,-5.0,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "130" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-7.5,-5.15,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-4.5,-5.0,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-4.5,-5.0,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "131" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-4.5,-5.15,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-1.5,-5.0,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-1.5,-5.0,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "132" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-1.5,-5.15,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <1.5,-5.0,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <1.5,-5.0,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "133" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <1.5,-5.15,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <4.5,-5.0,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <4.5,-5.0,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "134" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <4.5,-5.15,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <7.5,-5.0,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <7.5,-5.0,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "135" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <7.5,-5.15,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-9.0,-6.149999999999999,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-9.0,-6.149999999999999,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "136" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-9.0,-6.299999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-6.0,-6.149999999999999,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-6.0,-6.149999999999999,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "137" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-6.0,-6.299999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-3.0,-6.149999999999999,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-3.0,-6.149999999999999,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "138" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-3.0,-6.299999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <0.0,-6.149999999999999,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <0.0,-6.149999999999999,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "139" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0.0,-6.299999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <3.0,-6.149999999999999,4> texture {pigment {color rgb <0.01500000,0.10000000,0.34000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <3.0,-6.149999999999999,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "140" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <3.0,-6.299999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <6.0,-6.149999999999999,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <6.0,-6.149999999999999,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "141" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <6.0,-6.299999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <9.0,-6.149999999999999,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <9.0,-6.149999999999999,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "142" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <9.0,-6.299999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-7.5,-7.299999999999997,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-7.5,-7.299999999999997,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "143" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-7.5,-7.4499999999999975,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-4.5,-7.299999999999997,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-4.5,-7.299999999999997,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "144" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-4.5,-7.4499999999999975,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-1.5,-7.299999999999997,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-1.5,-7.299999999999997,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "145" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-1.5,-7.4499999999999975,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <1.5,-7.299999999999997,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <1.5,-7.299999999999997,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "146" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <1.5,-7.4499999999999975,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <4.5,-7.299999999999997,4> texture {pigment {color rgb <0.01500000,0.10000000,0.34000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <4.5,-7.299999999999997,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "147" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <4.5,-7.4499999999999975,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <7.5,-7.299999999999997,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <7.5,-7.299999999999997,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "148" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <7.5,-7.4499999999999975,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-9.0,-8.45,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-9.0,-8.45,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "149" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-9.0,-8.6,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-6.0,-8.45,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-6.0,-8.45,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "150" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-6.0,-8.6,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-3.0,-8.45,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-3.0,-8.45,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "151" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-3.0,-8.6,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <0.0,-8.45,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <0.0,-8.45,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "152" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0.0,-8.6,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <3.0,-8.45,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <3.0,-8.45,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "153" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <3.0,-8.6,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <6.0,-8.45,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <6.0,-8.45,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "154" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <6.0,-8.6,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <9.0,-8.45,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <9.0,-8.45,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "155" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <9.0,-8.6,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-7.5,-9.599999999999998,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-7.5,-9.599999999999998,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "156" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-7.5,-9.749999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-4.5,-9.599999999999998,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-4.5,-9.599999999999998,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "157" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-4.5,-9.749999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-1.5,-9.599999999999998,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-1.5,-9.599999999999998,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "158" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-1.5,-9.749999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <1.5,-9.599999999999998,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <1.5,-9.599999999999998,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "159" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <1.5,-9.749999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <4.5,-9.599999999999998,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <4.5,-9.599999999999998,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "160" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <4.5,-9.749999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <7.5,-9.599999999999998,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <7.5,-9.599999999999998,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "161" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <7.5,-9.749999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-9.0,-10.749999999999996,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-9.0,-10.749999999999996,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "162" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-9.0,-10.899999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-6.0,-10.749999999999996,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-6.0,-10.749999999999996,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "163" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-6.0,-10.899999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-3.0,-10.749999999999996,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-3.0,-10.749999999999996,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "164" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-3.0,-10.899999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <0.0,-10.749999999999996,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <0.0,-10.749999999999996,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "165" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0.0,-10.899999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <3.0,-10.749999999999996,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <3.0,-10.749999999999996,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "166" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <3.0,-10.899999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <6.0,-10.749999999999996,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <6.0,-10.749999999999996,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "167" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <6.0,-10.899999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <9.0,-10.749999999999996,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <9.0,-10.749999999999996,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "168" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <9.0,-10.899999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-7.5,-11.899999999999999,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-7.5,-11.899999999999999,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "169" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-7.5,-12.049999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-4.5,-11.899999999999999,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-4.5,-11.899999999999999,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "170" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-4.5,-12.049999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-1.5,-11.899999999999999,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-1.5,-11.899999999999999,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "171" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-1.5,-12.049999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <1.5,-11.899999999999999,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <1.5,-11.899999999999999,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "172" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <1.5,-12.049999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <4.5,-11.899999999999999,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <4.5,-11.899999999999999,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "173" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <4.5,-12.049999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <7.5,-11.899999999999999,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <7.5,-11.899999999999999,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "174" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <7.5,-12.049999999999999,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-9.0,-13.049999999999997,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-9.0,-13.049999999999997,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "175" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-9.0,-13.199999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-6.0,-13.049999999999997,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-6.0,-13.049999999999997,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "176" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-6.0,-13.199999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-3.0,-13.049999999999997,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-3.0,-13.049999999999997,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "177" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-3.0,-13.199999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <0.0,-13.049999999999997,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <0.0,-13.049999999999997,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "178" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0.0,-13.199999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <3.0,-13.049999999999997,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <3.0,-13.049999999999997,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "179" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <3.0,-13.199999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <6.0,-13.049999999999997,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <6.0,-13.049999999999997,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "180" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <6.0,-13.199999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <9.0,-13.049999999999997,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <9.0,-13.049999999999997,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "181" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <9.0,-13.199999999999998,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-7.5,-14.199999999999996,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-7.5,-14.199999999999996,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "182" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-7.5,-14.349999999999996,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-4.5,-14.199999999999996,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-4.5,-14.199999999999996,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "183" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-4.5,-14.349999999999996,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-1.5,-14.199999999999996,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-1.5,-14.199999999999996,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "184" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-1.5,-14.349999999999996,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <1.5,-14.199999999999996,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <1.5,-14.199999999999996,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "185" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <1.5,-14.349999999999996,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <4.5,-14.199999999999996,4> texture {pigment {color rgb <0.01500000,0.10000000,0.34000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <4.5,-14.199999999999996,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "186" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <4.5,-14.349999999999996,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <7.5,-14.199999999999996,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <7.5,-14.199999999999996,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "187" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <7.5,-14.349999999999996,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-9.0,-15.349999999999994,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-9.0,-15.349999999999994,4.04> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "188" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-9.0,-15.499999999999995,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-6.0,-15.349999999999994,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-6.0,-15.349999999999994,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "189" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-6.0,-15.499999999999995,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-3.0,-15.349999999999994,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-3.0,-15.349999999999994,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "190" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-3.0,-15.499999999999995,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <0.0,-15.349999999999994,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <0.0,-15.349999999999994,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "191" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0.0,-15.499999999999995,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <3.0,-15.349999999999994,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <3.0,-15.349999999999994,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "192" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <3.0,-15.499999999999995,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <6.0,-15.349999999999994,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <6.0,-15.349999999999994,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "193" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <6.0,-15.499999999999995,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <9.0,-15.349999999999994,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <9.0,-15.349999999999994,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "194" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <9.0,-15.499999999999995,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-7.5,-16.5,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-7.5,-16.5,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "195" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-7.5,-16.65,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-4.5,-16.5,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-4.5,-16.5,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "196" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-4.5,-16.65,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-1.5,-16.5,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-1.5,-16.5,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "197" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-1.5,-16.65,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <1.5,-16.5,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <1.5,-16.5,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "198" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <1.5,-16.65,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <4.5,-16.5,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <4.5,-16.5,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "199" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <4.5,-16.65,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <7.5,-16.5,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <7.5,-16.5,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "200" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <7.5,-16.65,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-9.0,-17.65,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-9.0,-17.65,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "201" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-9.0,-17.799999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-6.0,-17.65,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-6.0,-17.65,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "202" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-6.0,-17.799999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <-3.0,-17.65,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <-3.0,-17.65,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "203" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-3.0,-17.799999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <0.0,-17.65,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <0.0,-17.65,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "204" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0.0,-17.799999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <3.0,-17.65,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <3.0,-17.65,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "205" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <3.0,-17.799999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <6.0,-17.65,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <6.0,-17.65,4.04> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "206" .002,0 scale 0.43 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <6.0,-17.799999999999997,10>}
sphere{<0,0,0>,1 scale <1.04,.46,.025> translate <9.0,-17.65,4> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <.94,.38,.025> translate <9.0,-17.65,4.04> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}}}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "207" .002,0 scale 0.43 texture {pigment {color rgb <1.00000000,1.00000000,1.00000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <9.0,-17.799999999999997,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "0" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,17.86,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "1" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,16.71,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "2" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,15.559999999999999,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "3" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,14.41,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "4" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,13.26,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "5" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,12.11,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "6" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,10.96,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "7" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,9.81,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "8" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,8.66,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "9" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,7.510000000000001,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "10" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,6.36,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "11" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,5.210000000000002,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "12" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,4.060000000000001,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "13" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,2.9100000000000006,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "14" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,1.760000000000002,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "15" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,0.61,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "16" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,-0.5399999999999986,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "17" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,-1.6899999999999973,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "18" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,-2.8399999999999994,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "19" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,-3.989999999999998,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "20" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,-5.14,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "21" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,-6.289999999999998,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "22" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,-7.439999999999997,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "23" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,-8.59,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "24" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,-9.739999999999998,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "25" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,-10.889999999999997,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "26" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,-12.04,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "27" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,-13.189999999999998,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "28" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,-14.339999999999996,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "29" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,-15.489999999999995,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "30" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,-16.64,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "31" .002,0 scale 0.36 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-max_extent(T).x,0,0> translate <-13.5,-17.79,10>}
cylinder{<-11.5,18.62,3>,<11.5,18.62,3>,0.047 texture {pigment {color rgb <0.00200000,0.16000000,0.19000000>} finish {ambient 1 diffuse 0}} no_shadow}
cylinder{<-11.5,-18.27,3>,<11.5,-18.27,3>,0.047 texture {pigment {color rgb <0.12000000,0.02000000,0.26000000>} finish {ambient 1 diffuse 0}} no_shadow}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "START 0" .002,0 scale 0.34 texture {pigment {color rgb <0.00200000,0.16000000,0.19000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-min_extent(T).x,0,0> translate <12.6,18.5,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "END 208" .002,0 scale 0.3 texture {pigment {color rgb <0.12000000,0.02000000,0.26000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-min_extent(T).x,0,0> translate <12.6,-18.25,10>}
sphere{<0,0,0>,1 scale <0.2,0.2,.025> translate <-4.5,-19.86,4> texture {pigment {color rgb <0.66000000,0.02500000,0.04500000>} finish {ambient 1 diffuse 0}} no_shadow}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "red" .002,0 scale 0.45 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-min_extent(T).x,0,0> translate <-4.1,-20,10>}
sphere{<0,0,0>,1 scale <0.2,0.2,.025> translate <-1.1,-19.86,4> texture {pigment {color rgb <1.00000000,0.65000000,0.02500000>} finish {ambient 1 diffuse 0}} no_shadow}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "yellow" .002,0 scale 0.45 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-min_extent(T).x,0,0> translate <-0.6999999999999997,-20,10>}
sphere{<0,0,0>,1 scale <0.2,0.2,.025> translate <2.3,-19.86,4> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}} no_shadow}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "black" .002,0 scale 0.45 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-min_extent(T).x,0,0> translate <2.7,-20,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "Blue outline: 43, 75, 82, 89, 140, 147, 186. All seven have observations." .002,0 scale 0.35 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0,-21.7,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "Page-down row direction; +1 right, +6 down-left, +7 down-right." .002,0 scale 0.37 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0,-22.7,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "Display convention only. Authentic chart, count and physical topology unverified." .002,0 scale 0.35 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0,-23.7,10>}
