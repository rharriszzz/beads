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


camera {orthographic location <33.4856746795,-0,72.6547286228> direction <-0.418570933494,0,-0.908184107785> right <23.7438222026,-30.2733624454,-10.9432368821> up <-19.2456506635,-18.3009980018,8.87008470515> }
background {color rgb <0.23,0.29,0.34>}
light_source {<53.4583406896,46.9807574071,80> color rgb 1.2492432548525017 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.23,0.29,0.34>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,3.71487181319,-1.48314780503>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,3.33089442998,2.21475558389>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,0.069455588316,3.9993969447>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,-3.2519838876,2.32907724105>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,-3.76413039529,-1.35326359859>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,-1.02455567172,-3.86655992784>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,2.60010247895,-3.03964917366>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,3.97860878408,0.41312485186>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,1.92011230359,3.50901250234>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-1.79711256521,3.57356774498>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,-3.961864892,0.551023209614>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,-2.7040789877,-2.94753402495>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,0.88968100142,-3.89980354835>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,3.71487181319,-1.48314780503>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,3.33089442998,2.21475558389>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,0.069455588316,3.9993969447>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,-3.2519838876,2.32907724105>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,-3.76413039529,-1.35326359859>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,-1.02455567172,-3.86655992784>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,2.60010247895,-3.03964917366>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,3.97860878408,0.41312485186>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,-1.79711256521,3.57356774498>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,-3.961864892,0.551023209614>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,-2.7040789877,-2.94753402495>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,0.88968100142,-3.89980354835>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,3.71487181319,-1.48314780503>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,3.33089442998,2.21475558389>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.7 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,0.069455588316,3.9993969447>}