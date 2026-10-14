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


camera {orthographic location <-0.997317731847,0,79.9937832418> direction <0.0124664716481,-0,-0.999922290523> right <39.7210727031,-4.68947122328,0.495220109981> up <-3.28237476485,-27.8069117528,-0.0409228120347> }
background {color rgb <0.23,0.29,0.34>}
light_source {<-50.7550589246,20.312021333,80> color rgb 1.059572367096552 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.23,0.29,0.34>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,0.0944593592716,3.99888452314>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,-3.23735841212,2.34936385251>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,-3.77251773219,-1.32970295943>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,-1.04871024803,-3.86007860227>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,2.58104708931,-3.05584618768>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,3.9811139702,0.388241620954>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,1.94201390908,3.49693894384>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,-1.77473469139,3.58473384998>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,-3.95834233503,0.575782909335>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-2.72245478067,-2.93056990485>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,0.865281164102,-3.90528981089>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,3.70552623134,-1.50634502982>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,3.34467647612,2.19388679518>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,0.0944593592716,3.99888452314>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.23735841212,2.34936385251>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,-3.77251773219,-1.32970295943>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,-1.04871024803,-3.86007860227>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,2.58104708931,-3.05584618768>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,3.9811139702,0.388241620954>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,1.94201390908,3.49693894384>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,-1.77473469139,3.58473384998>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,-3.95834233503,0.575782909335>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,-2.72245478067,-2.93056990485>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,0.865281164101,-3.90528981089>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,3.70552623134,-1.50634502982>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,3.34467647612,2.19388679518>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,0.0944593592716,3.99888452314>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,-3.23735841212,2.34936385251>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.12 diffuse .75 specular 0.3 roughness 0.035}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,-3.77251773219,-1.32970295943>}