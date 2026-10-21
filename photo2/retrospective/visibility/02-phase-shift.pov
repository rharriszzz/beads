#version 3.7;
global_settings {assumed_gamma 1 max_trace_level 12 ambient_light rgb 1}
background {color rgb 1}
camera {orthographic location <0,0,200> direction <0,0,-1>
 right x*36 up y*20}
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
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "ONE EXTRA BEAD CHANGES THE ALIGNMENT" .002,0 scale 0.73 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0,8.45,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "Track the same black pattern position: p = 3" .002,0 scale 0.48 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0,7.25,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "L = 26" .002,0 scale 0.65 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-min_extent(T).x,0,0> translate <-17,4.7,10>}
torus{2,.027 rotate <90,0,0> translate <-10.3,2.9,3> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-10.3,4.9,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-8.654032268212688,4.036129493462312,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-8.42996751462917,2.1907902259149292,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-9.821368671424885,0.9581163651478959,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-11.62624531648159,1.4029785036577973,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-12.285417748196108,3.1410733605106462,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-11.229446344087538,4.67091205130642,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-9.370553655912465,4.67091205130642,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-8.314582251803893,3.141073360510647,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-8.97375468351841,1.4029785036577986,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-10.778631328575116,0.9581163651478961,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-12.170032485370829,2.1907902259149243,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-11.945967731787313,4.036129493462312,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.37,0.37,.025> translate <-9.821368671424885,0.9581163651478959,3.97> texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.3,0.3,.025> translate <-9.821368671424885,0.9581163651478959,4> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}} no_shadow}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "copy 0: phase 3" .002,0 scale 0.4 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-10.3,-0.050000000000000266,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "rear: skip" .002,0 scale 0.42 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-10.3,5.65,10>}
torus{2,.027 rotate <90,0,0> translate <-2.500000000000001,2.9,3> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-2.500000000000001,4.9,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-0.8540322682126882,4.036129493462312,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-0.6299675146291712,2.1907902259149292,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-2.0213686714248853,0.9581163651478959,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-3.826245316481591,1.4029785036577973,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-4.485417748196109,3.1410733605106462,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-3.4294463440875376,4.67091205130642,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-1.570553655912465,4.67091205130642,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-0.5145822518038932,3.141073360510647,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-1.1737546835184096,1.4029785036577986,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-2.978631328575117,0.9581163651478961,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-4.370032485370829,2.1907902259149243,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-4.145967731787313,4.036129493462312,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.37,0.37,.025> translate <-2.0213686714248853,0.9581163651478959,3.97> texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.3,0.3,.025> translate <-2.0213686714248853,0.9581163651478959,4> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}} no_shadow}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "copy 1: phase 3" .002,0 scale 0.4 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-2.500000000000001,-0.050000000000000266,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "rear: skip" .002,0 scale 0.42 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-2.500000000000001,5.65,10>}
torus{2,.027 rotate <90,0,0> translate <5.299999999999999,2.9,3> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <5.299999999999999,4.9,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <6.945967731787311,4.036129493462312,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <7.170032485370829,2.1907902259149292,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <5.7786313285751145,0.9581163651478959,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <3.973754683518409,1.4029785036577973,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <3.314582251803891,3.1410733605106462,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <4.370553655912462,4.67091205130642,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <6.229446344087535,4.67091205130642,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <7.285417748196107,3.141073360510647,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <6.62624531648159,1.4029785036577986,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <4.8213686714248825,0.9581163651478961,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <3.429967514629171,2.1907902259149243,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <3.6540322682126867,4.036129493462312,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.37,0.37,.025> translate <5.7786313285751145,0.9581163651478959,3.97> texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.3,0.3,.025> translate <5.7786313285751145,0.9581163651478959,4> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}} no_shadow}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "copy 2: phase 3" .002,0 scale 0.4 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <5.299999999999999,-0.050000000000000266,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "rear: skip" .002,0 scale 0.42 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <5.299999999999999,5.65,10>}
torus{2,.027 rotate <90,0,0> translate <13.099999999999998,2.9,3> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <13.099999999999998,4.9,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <14.74596773178731,4.036129493462312,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <14.970032485370828,2.1907902259149292,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <13.578631328575113,0.9581163651478959,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <11.773754683518408,1.4029785036577973,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <11.11458225180389,3.1410733605106462,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <12.17055365591246,4.67091205130642,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <14.029446344087534,4.67091205130642,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <15.085417748196106,3.141073360510647,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <14.42624531648159,1.4029785036577986,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <12.621368671424882,0.9581163651478961,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <11.22996751462917,2.1907902259149243,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <11.454032268212686,4.036129493462312,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.37,0.37,.025> translate <13.578631328575113,0.9581163651478959,3.97> texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.3,0.3,.025> translate <13.578631328575113,0.9581163651478959,4> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}} no_shadow}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "copy 3: phase 3" .002,0 scale 0.4 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <13.099999999999998,-0.050000000000000266,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "rear: skip" .002,0 scale 0.42 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <13.099999999999998,5.65,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "L = 27" .002,0 scale 0.65 texture {pigment {color rgb <0.00200000,0.16000000,0.19000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-min_extent(T).x,0,0> translate <-17,-1.8499999999999999,10>}
torus{2,.027 rotate <90,0,0> translate <-10.3,-3.65,3> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-10.3,-1.65,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-8.654032268212688,-2.513870506537688,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-8.42996751462917,-4.359209774085071,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-9.821368671424885,-5.591883634852104,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-11.62624531648159,-5.1470214963422025,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-12.285417748196108,-3.4089266394893536,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-11.229446344087538,-1.8790879486935799,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-9.370553655912465,-1.8790879486935794,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-8.314582251803893,-3.4089266394893527,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-8.97375468351841,-5.147021496342202,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-10.778631328575116,-5.5918836348521035,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-12.170032485370829,-4.359209774085075,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-11.945967731787313,-2.5138705065376876,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.37,0.37,.025> translate <-9.821368671424885,-5.591883634852104,3.97> texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.3,0.3,.025> translate <-9.821368671424885,-5.591883634852104,4> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}} no_shadow}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "copy 0: phase 3" .002,0 scale 0.4 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-10.3,-6.6,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "rear: skip" .002,0 scale 0.42 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-10.3,-0.8999999999999999,10>}
torus{2,.027 rotate <90,0,0> translate <-2.500000000000001,-3.65,3> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-2.500000000000001,-1.65,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-0.8540322682126882,-2.513870506537688,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-0.6299675146291712,-4.359209774085071,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-2.0213686714248853,-5.591883634852104,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-3.826245316481591,-5.1470214963422025,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-4.485417748196109,-3.4089266394893536,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-3.4294463440875376,-1.8790879486935799,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-1.570553655912465,-1.8790879486935794,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-0.5145822518038932,-3.4089266394893527,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-1.1737546835184096,-5.147021496342202,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-2.978631328575117,-5.5918836348521035,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-4.370032485370829,-4.359209774085075,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <-4.145967731787313,-2.5138705065376876,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.37,0.37,.025> translate <-3.826245316481591,-5.1470214963422025,3.97> texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.3,0.3,.025> translate <-3.826245316481591,-5.1470214963422025,4> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}} no_shadow}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "copy 1: phase 4" .002,0 scale 0.4 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-2.500000000000001,-6.6,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "rear: skip" .002,0 scale 0.42 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <-2.500000000000001,-0.8999999999999999,10>}
torus{2,.027 rotate <90,0,0> translate <5.299999999999999,-3.65,3> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <5.299999999999999,-1.65,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <6.945967731787311,-2.513870506537688,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <7.170032485370829,-4.359209774085071,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <5.7786313285751145,-5.591883634852104,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <3.973754683518409,-5.1470214963422025,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <3.314582251803891,-3.4089266394893536,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <4.370553655912462,-1.8790879486935799,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <6.229446344087535,-1.8790879486935794,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <7.285417748196107,-3.4089266394893527,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <6.62624531648159,-5.147021496342202,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <4.8213686714248825,-5.5918836348521035,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <3.429967514629171,-4.359209774085075,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <3.6540322682126867,-2.5138705065376876,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.37,0.37,.025> translate <3.314582251803891,-3.4089266394893536,3.97> texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.3,0.3,.025> translate <3.314582251803891,-3.4089266394893536,4> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}} no_shadow}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "copy 2: phase 5" .002,0 scale 0.4 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <5.299999999999999,-6.6,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "edge: skip" .002,0 scale 0.42 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <5.299999999999999,-0.8999999999999999,10>}
torus{2,.027 rotate <90,0,0> translate <13.099999999999998,-3.65,3> texture {pigment {color rgb <0.68000000,0.73000000,0.76000000>} finish {ambient 1 diffuse 0}}}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <13.099999999999998,-1.65,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <14.74596773178731,-2.513870506537688,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <14.970032485370828,-4.359209774085071,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <13.578631328575113,-5.591883634852104,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <11.773754683518408,-5.1470214963422025,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <11.11458225180389,-3.4089266394893536,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <12.17055365591246,-1.8790879486935799,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <14.029446344087534,-1.8790879486935794,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <15.085417748196106,-3.4089266394893527,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <14.42624531648159,-5.147021496342202,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <12.621368671424882,-5.5918836348521035,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <11.22996751462917,-4.359209774085075,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.13,0.13,.025> translate <11.454032268212686,-2.5138705065376876,4> texture {pigment {color rgb <0.91000000,0.94000000,0.95000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.37,0.37,.025> translate <12.17055365591246,-1.8790879486935799,3.97> texture {pigment {color rgb <0.00200000,0.16000000,0.19000000>} finish {ambient 1 diffuse 0}} no_shadow}
sphere{<0,0,0>,1 scale <0.3,0.3,.025> translate <12.17055365591246,-1.8790879486935799,4> texture {pigment {color rgb <0.01800000,0.02500000,0.03500000>} finish {ambient 1 diffuse 0}} no_shadow}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "copy 3: phase 6" .002,0 scale 0.4 texture {pigment {color rgb <0.01800000,0.04000000,0.06500000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <13.099999999999998,-6.6,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "READ" .002,0 scale 0.42 texture {pigment {color rgb <0.00200000,0.16000000,0.19000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <13.099999999999998,-0.8999999999999999,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "Front is at the TOP of each end-on diagram. The black disk is a known target," .002,0 scale 0.39 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0,-8.15,10>}
#local T=text {ttf "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" "not a color measurement through the tube. Phase arithmetic; not an optical image." .002,0 scale 0.39 texture {pigment {color rgb <0.07500000,0.10500000,0.14000000>} finish {ambient 1 diffuse 0}} no_shadow};
object{T translate <-(min_extent(T).x+max_extent(T).x)/2,0,0> translate <0,-9.05,10>}
