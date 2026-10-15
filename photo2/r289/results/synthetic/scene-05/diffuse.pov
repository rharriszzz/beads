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


camera {orthographic location <33.8094609393,-0,72.5046229629> direction <-0.422618261741,0,-0.906307787037> right <27.9350147995,-17.7242120307,-13.0263113317> up <-11.2445139678,-21.5760149469,5.2434029754> }
background {color rgb <0.47,0.31,0.43>}
light_source {<56,-32,80> color rgb 0.55 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,0.103899040118,3.998650396>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,3.34984614317,2.18598509077>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,3.7019599617,-1.51508826211>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,0.856059752933,-3.90732155055>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,-2.72936522823,-2.92413499192>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,-3.95697208715,0.585125543371>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,-1.76626746479,3.58891337912>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,1.95026352706,3.49234479613>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,3.98201937791,0.378842545101>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,2.57382613172,-3.06193060726>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,-1.05781959861,-3.85759221494>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,-3.77564617647,-1.32079368189>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,-3.23180337935,2.35699955817>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,0.103899040118,3.998650396>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0,3.34984614317,2.18598509077>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,3.7019599617,-1.51508826211>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,0.856059752933,-3.90732155055>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,-2.72936522823,-2.92413499192>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,-3.95697208715,0.585125543371>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,-1.76626746479,3.58891337912>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,1.95026352706,3.49234479613>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,3.98201937791,0.378842545101>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,2.57382613172,-3.06193060726>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,-1.05781959861,-3.85759221494>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,-3.77564617647,-1.32079368189>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,-3.23180337935,2.35699955817>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,0.103899040118,3.998650396>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,3.34984614317,2.18598509077>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.06}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,3.7019599617,-1.51508826211>}
