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


camera {orthographic location <14.8277933124,0.711523747899,99.153878153> direction <-0.076827329544,0,-0.99704441297> right <28.2049439719,-4.96923828154,-2.17333400309> up <-3.89286170847,-22.2267204131,0.299964741245> }
background {color rgb <.47,.31,.43>}
light_source {<-250.464697791,474.117320004,844.085423422> color rgb 1.1 parallel point_at <0,0,0>}
plane {z,-6 pigment {color rgb <.47,.31,.43>} finish {ambient .12 diffuse .8}}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-28.7810364081,-2.07204397045,3.4214958402>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-28.3313327142,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-27.8816290203,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-27.4319253264,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-26.9822216326,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-26.5325179387,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-26.0828142448,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-25.6331105509,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-25.1834068571,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-24.7337031632,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-24.2839994693,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-23.8342957754,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-23.3845920816,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-22.9348883877,-2.07204397045,3.4214958402>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-22.4851846938,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-22.0354809999,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-21.5857773061,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-21.1360736122,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-20.6863699183,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-20.2366662244,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-19.7869625305,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-19.3372588367,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-18.8875551428,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-18.4378514489,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-17.988147755,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-17.5384440612,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-17.0887403673,-2.07204397045,3.4214958402>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-16.6390366734,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-16.1893329795,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-15.7396292857,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-15.2899255918,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-14.8402218979,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-14.390518204,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-13.9408145102,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-13.4911108163,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-13.0414071224,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-12.5917034285,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-12.1419997347,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-11.6922960408,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-11.2425923469,-2.07204397045,3.42149584021>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-10.792888653,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-10.3431849591,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-9.89348126527,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-9.4437775714,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-8.99407387752,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-8.54437018365,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-8.09466648977,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-7.64496279589,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-7.19525910202,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-6.74555540814,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-6.29585171427,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-5.84614802039,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-5.39644432651,-2.07204397045,3.4214958402>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-4.94674063264,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703693876,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-4.04733324488,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762955101,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792585713,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-2.69822216326,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851846938,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-1.7988147755,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-1.34911108163,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-0.899407387752,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703693876,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <0,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <0.449703693876,-2.07204397045,3.4214958402>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <0.899407387752,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <1.34911108163,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <1.7988147755,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <2.24851846938,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <2.69822216326,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <3.14792585713,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <3.59762955101,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <4.04733324488,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <4.49703693876,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <4.94674063264,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <5.39644432651,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <5.84614802039,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <6.29585171427,-2.07204397045,3.42149584021>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <6.74555540814,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <7.19525910202,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <7.64496279589,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <8.09466648977,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <8.54437018365,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <8.99407387752,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <9.4437775714,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <9.89348126527,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <10.3431849591,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <10.792888653,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <11.2425923469,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <11.6922960408,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <12.1419997347,-2.07204397045,3.42149584021>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <12.5917034285,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <13.0414071224,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <13.4911108163,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <13.9408145102,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <14.390518204,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <14.8402218979,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <15.2899255918,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <15.7396292857,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <16.1893329795,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.95,0.65,0.015>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <16.6390366734,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <17.0887403673,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <17.5384440612,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <17.988147755,-2.07204397045,3.4214958402>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <18.4378514489,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.012,0.012,0.012>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <18.8875551428,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.65,0.025,0.008>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <19.3372588367,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <19.7869625305,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <20.2366662244,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <20.6863699183,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <21.1360736122,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <21.5857773061,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <22.0354809999,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <22.4851846938,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <22.9348883877,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <23.3845920816,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <23.8342957754,-2.07204397045,3.4214958402>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <24.2839994693,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <24.7337031632,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <25.1834068571,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <25.6331105509,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <26.0828142448,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <26.5325179387,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <26.9822216326,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <27.4319253264,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <27.8816290203,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <28.3313327142,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.35,0.35,0.35>} finish {ambient .1 diffuse .75 specular 1.2 roughness .035}}},.8,.7,1) rotate <0,0,-90> translate <28.7810364081,3.93391110296,0.724115621993>}