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


camera {orthographic location <-33.8094609393,0,72.5046229629> direction <0.422618261741,-0,-0.906307787037> right <28.4064344227,-16.7872524455,13.2461379122> up <-10.65009233,-21.9401227489,-4.96621961353> }
background {color rgb <0.47,0.31,0.43>}
light_source {<-32,40,80> color rgb 0.55 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <0.47,0.31,0.43>} finish {ambient .18 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584646773,-3.84193958077,1.11332845905>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.8461431486,-3.09872179414,-2.52941163959>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643982948,0.32139035841,-3.9870676239>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673651036,3.46386285925,-2.00041348034>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703319123,3.61400639729,1.71433886976>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732987211,0.642116398274,3.94812443206>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762655299,-2.88447901897,2.77124174137>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792323386,-3.919258085,-0.799634956181>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821991474,-1.56830568389,-3.67973059909>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851659562,2.13745974277,-3.38101550544>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881327649,3.99673673874,-0.161540834495>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910995737,2.40335074372,3.19748419897>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.899406638247,-1.26621907567,3.79429693783>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703319123,-3.84193958077,1.11332845905>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.09872179414,-2.52941163959>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.449703319123,0.32139035841,-3.9870676239>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <0.899406638247,3.46386285925,-2.00041348034>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.34910995737,3.61400639729,1.71433886976>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <1.79881327649,0.642116398275,3.94812443206>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.24851659562,-2.88447901897,2.77124174137>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <2.69821991474,-3.919258085,-0.799634956181>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.14792323386,-1.56830568389,-3.67973059909>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <3.59762655299,2.13745974277,-3.38101550544>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.04732987211,3.99673673874,-0.161540834495>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.49703319123,2.40335074372,3.19748419897>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <4.94673651036,-1.26621907567,3.79429693783>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.39643982948,-3.84193958077,1.11332845905>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <5.8461431486,-3.09872179414,-2.52941163959>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient 0.08 diffuse .75 specular 0 roughness 0.025}}},.8,.7,1) rotate <0,0,-90> translate <6.29584646773,0.32139035841,-3.9870676239>}
