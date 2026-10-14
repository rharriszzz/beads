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
background {color rgb 0}
object {bead(material {texture {pigment {color rgb <0.00392156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-28.7810364081,-2.07204397045,3.4214958402>}
object {bead(material {texture {pigment {color rgb <0.0078431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-28.3313327142,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.0117647058824,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-27.8816290203,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.0156862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-27.4319253264,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.0196078431373,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-26.9822216326,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.0235294117647,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-26.5325179387,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.0274509803922,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-26.0828142448,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.0313725490196,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-25.6331105509,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.0352941176471,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-25.1834068571,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.0392156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-24.7337031632,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.043137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-24.2839994693,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.0470588235294,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-23.8342957754,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.0509803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-23.3845920816,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.0549019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-22.9348883877,-2.07204397045,3.4214958402>}
object {bead(material {texture {pigment {color rgb <0.0588235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-22.4851846938,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.0627450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-22.0354809999,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.0666666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-21.5857773061,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.0705882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-21.1360736122,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.0745098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-20.6863699183,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.078431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-20.2366662244,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.0823529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-19.7869625305,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.0862745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-19.3372588367,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.0901960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-18.8875551428,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.0941176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-18.4378514489,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.0980392156863,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-17.988147755,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.101960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-17.5384440612,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.105882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-17.0887403673,-2.07204397045,3.4214958402>}
object {bead(material {texture {pigment {color rgb <0.109803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-16.6390366734,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.113725490196,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-16.1893329795,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.117647058824,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-15.7396292857,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.121568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-15.2899255918,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.125490196078,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-14.8402218979,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.129411764706,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-14.390518204,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.133333333333,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-13.9408145102,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.137254901961,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-13.4911108163,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.141176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-13.0414071224,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.145098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-12.5917034285,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.149019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-12.1419997347,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.152941176471,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-11.6922960408,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.156862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-11.2425923469,-2.07204397045,3.42149584021>}
object {bead(material {texture {pigment {color rgb <0.160784313725,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-10.792888653,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.164705882353,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-10.3431849591,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.16862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-9.89348126527,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.172549019608,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-9.4437775714,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.176470588235,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-8.99407387752,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.180392156863,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-8.54437018365,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.18431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-8.09466648977,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.188235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-7.64496279589,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.192156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-7.19525910202,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.196078431373,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-6.74555540814,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.2,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-6.29585171427,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.203921568627,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.84614802039,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.207843137255,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.39644432651,-2.07204397045,3.4214958402>}
object {bead(material {texture {pigment {color rgb <0.211764705882,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.94674063264,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.21568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.49703693876,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.219607843137,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.04733324488,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.223529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762955101,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.227450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792585713,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.23137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.69822216326,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.235294117647,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851846938,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.239215686275,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.7988147755,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.243137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.34911108163,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.247058823529,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.899407387752,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.250980392157,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.449703693876,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.254901960784,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.258823529412,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.449703693876,-2.07204397045,3.4214958402>}
object {bead(material {texture {pigment {color rgb <0.262745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.899407387752,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.266666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.34911108163,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.270588235294,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.7988147755,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.274509803922,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.24851846938,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.278431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.69822216326,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.282352941176,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.14792585713,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.286274509804,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.59762955101,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.290196078431,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.04733324488,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.294117647059,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.49703693876,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.298039215686,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.94674063264,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.301960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.39644432651,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.305882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.84614802039,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.309803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <6.29585171427,-2.07204397045,3.42149584021>}
object {bead(material {texture {pigment {color rgb <0.313725490196,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <6.74555540814,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.317647058824,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <7.19525910202,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.321568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <7.64496279589,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.325490196078,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <8.09466648977,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.329411764706,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <8.54437018365,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.333333333333,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <8.99407387752,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.337254901961,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <9.4437775714,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.341176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <9.89348126527,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.345098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <10.3431849591,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.349019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <10.792888653,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.352941176471,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <11.2425923469,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.356862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <11.6922960408,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.360784313725,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <12.1419997347,-2.07204397045,3.42149584021>}
object {bead(material {texture {pigment {color rgb <0.364705882353,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <12.5917034285,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.36862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <13.0414071224,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.372549019608,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <13.4911108163,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.376470588235,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <13.9408145102,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.380392156863,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <14.390518204,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.38431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <14.8402218979,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.388235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <15.2899255918,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.392156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <15.7396292857,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.396078431373,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <16.1893329795,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.4,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <16.6390366734,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.403921568627,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <17.0887403673,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.407843137255,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <17.5384440612,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.411764705882,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <17.988147755,-2.07204397045,3.4214958402>}
object {bead(material {texture {pigment {color rgb <0.41568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <18.4378514489,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.419607843137,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <18.8875551428,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.423529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <19.3372588367,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.427450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <19.7869625305,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.43137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <20.2366662244,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.435294117647,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <20.6863699183,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.439215686275,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <21.1360736122,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.443137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <21.5857773061,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.447058823529,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <22.0354809999,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.450980392157,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <22.4851846938,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.454901960784,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <22.9348883877,3.93391110296,0.724115621993>}
object {bead(material {texture {pigment {color rgb <0.458823529412,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <23.3845920816,1.63878074042,3.64888992501>}
object {bead(material {texture {pigment {color rgb <0.462745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <23.8342957754,-2.07204397045,3.4214958402>}
object {bead(material {texture {pigment {color rgb <0.466666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <24.2839994693,-3.992891007,0.238372410809>}
object {bead(material {texture {pigment {color rgb <0.470588235294,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <24.7337031632,-2.46439726679,-3.15067391386>}
object {bead(material {texture {pigment {color rgb <0.474509803922,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <25.1834068571,1.1930165886,-3.81794596862>}
object {bead(material {texture {pigment {color rgb <0.478431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <25.6331105509,3.81981859928,-1.18700710554>}
object {bead(material {texture {pigment {color rgb <0.482352941176,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <26.0828142448,3.14679198172,2.46935218707>}
object {bead(material {texture {pigment {color rgb <0.486274509804,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <26.5325179387,-0.244655419055,3.99251095502>}
object {bead(material {texture {pigment {color rgb <0.490196078431,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <26.9822216326,-3.42475221904,2.0666572619>}
object {bead(material {texture {pigment {color rgb <0.494117647059,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <27.4319253264,-3.6463065848,-1.6445206869>}
object {bead(material {texture {pigment {color rgb <0.498039215686,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <27.8816290203,-0.717924234155,-3.93504571689>}
object {bead(material {texture {pigment {color rgb <0.501960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <28.3313327142,2.83065168831,-2.82620081018>}
object {bead(material {texture {pigment {color rgb <0.505882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <28.7810364081,3.93391110296,0.724115621993>}