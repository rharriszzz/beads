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


camera {orthographic location <-11.8371641308,0,79.1194132014> direction <0.147964551636,-0,-0.988992665018> right <34.0037368825,7.33088328194,5.08734580115> up <5.07513285576,-24.0675352403,0.759297600533> }
background {color rgb <0.47,0.31,0.43>}
light_source {<36.4562056766,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,-3.26317985605,-2.31336491437>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,0.0501645619827,-3.99968542722>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,3.32017329445,-2.23079566407>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,3.72198224125,1.46521267939>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,0.908480503975,3.89546700331>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,-2.68983074645,2.96054227389>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,-3.96447654743,-0.531907609308>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,-1.81432798523,-3.56485819662>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,1.9031650126,-3.51823292788>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,3.97656988697,-0.432309997617>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,2.6147333188,3.02707278927>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,-1.00589424594,3.87145667236>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,-3.75755943892,1.37140331886>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,-3.26317985605,-2.31336491437>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <0,0.0501645619827,-3.99968542722>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,3.32017329445,-2.23079566407>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,3.72198224125,1.46521267939>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,0.908480503975,3.89546700331>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,-2.68983074645,2.96054227389>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,-3.96447654743,-0.531907609308>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,-1.81432798523,-3.56485819662>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,1.9031650126,-3.51823292788>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,3.97656988697,-0.432309997617>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,2.6147333188,3.02707278927>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,-1.00589424594,3.87145667236>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,-3.75755943892,1.37140331886>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,-3.26317985605,-2.31336491437>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,0.0501645619827,-3.99968542722>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.03 diffuse .75 specular 0.12 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,3.32017329445,-2.23079566407>}