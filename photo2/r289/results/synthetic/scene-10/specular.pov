#version 3.7;
global_settings {assumed_gamma 1.0}
#declare bead_radius=1.784536980648071;
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


camera {orthographic location <0,-0,80> direction <-0,0,-1> right <27.3351119449,-22.7373961971,-0> up <-15.916177338,-19.1345783614,-0> }
background {color rgb <0.47,0.31,0.43>}
light_source {<24,-72,44> color rgb 0.55 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient 0 diffuse 0}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,-2.21540090629,3.33046525645>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,-3.99941032672,0.0686807000433>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,-2.32844712235,-3.2524350875>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,1.35399287704,-3.76386812852>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,3.8667583639,-1.02380650282>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,3.03914534428,2.60069136507>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,-0.413895703349,3.97852866607>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,-3.50938446007,1.91943239304>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,-3.57321948563,-1.79780491364>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-0.550255584173,-3.96197157891>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,2.94805788751,-2.70350784942>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,3.89963109861,0.890436575374>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,1.48242801724,3.71515910476>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,-2.21540090629,3.33046525645>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.99941032672,0.0686807000433>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,-2.32844712235,-3.2524350875>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,1.35399287704,-3.76386812852>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,3.8667583639,-1.02380650282>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,3.03914534428,2.60069136507>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,-0.413895703349,3.97852866607>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,-3.50938446007,1.91943239304>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,-3.57321948563,-1.79780491364>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,-0.550255584173,-3.96197157891>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,2.94805788751,-2.70350784942>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,3.89963109861,0.890436575374>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,1.48242801724,3.71515910476>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,-2.21540090629,3.33046525645>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,-3.99941032672,0.0686807000433>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0 diffuse 0 specular 0.35 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,-2.32844712235,-3.2524350875>}
