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


camera {orthographic location <-32.5389314461,0,73.0836366114> direction <0.406736643076,-0,-0.913545457643> right <32.4699847932,0.951441805552,14.4565686415> up <0.608429737771,-24.879976322,0.27089037225> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-48,-64,80> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,1.48493532648,3.71415765365>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,-2.21315241419,3.33195984243>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,-3.99936305777,0.0713801943639>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,-2.3306419108,-3.25086269836>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,1.35145204421,-3.76478118517>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,3.86606643723,-1.02641624254>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,3.04090005881,2.59863941945>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,-0.411210193739,3.97880712985>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,-3.50808808793,1.92180070957>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,-3.57443214862,-1.79539266315>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,-0.552929698499,-3.96159926652>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,2.94623241035,-2.70549710483>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,3.90023123449,0.887804211253>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,1.48493532648,3.71415765365>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <0,-2.21315241419,3.33195984243>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,-3.99936305777,0.0713801943639>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,-2.3306419108,-3.25086269836>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,1.35145204421,-3.76478118517>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,3.86606643723,-1.02641624254>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,3.04090005881,2.59863941945>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,-0.411210193739,3.97880712985>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,-3.50808808793,1.92180070957>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,-3.57443214862,-1.79539266315>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,-0.552929698499,-3.96159926652>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,2.94623241035,-2.70549710483>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,3.90023123449,0.887804211253>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,1.48493532648,3.71415765365>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,-2.21315241419,3.33195984243>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.1 diffuse .75 specular 0.15 roughness 0.1}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,-3.99936305777,0.0713801943639>}
