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


camera {orthographic location <-14.9394224012,-0.69725834602,99.1452763609> direction <0.0768273574905,-0,-0.997044410817> right <-28.6016273304,6.07816401703,-2.20390127449> up <4.76158529095,22.5393241709,0.366904434146> }
background {color rgb 0}
object {bead(material {texture {pigment {color rgb <0.00392156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-18.1005735848,2.07204397561,3.42149583708>}
object {bead(material {texture {pigment {color rgb <0.0078431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-17.6480592452,-1.63878073492,3.64888992748>}
object {bead(material {texture {pigment {color rgb <0.0117647058824,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-17.1955449056,-3.93391110187,0.724115627929>}
object {bead(material {texture {pigment {color rgb <0.0156862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-16.743030566,-2.83065169257,-2.82620080591>}
object {bead(material {texture {pigment {color rgb <0.0196078431373,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-16.2905162263,0.717924228217,-3.93504571797>}
object {bead(material {texture {pigment {color rgb <0.0235294117647,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-15.8380018867,3.64630658232,-1.6445206924>}
object {bead(material {texture {pigment {color rgb <0.0274509803922,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-15.3854875471,3.42475222216,2.06665725673>}
object {bead(material {texture {pigment {color rgb <0.0313725490196,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-14.9329732075,0.244655425079,3.99251095465>}
object {bead(material {texture {pigment {color rgb <0.0352941176471,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-14.4804588679,-3.14679197799,2.46935219182>}
object {bead(material {texture {pigment {color rgb <0.0392156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-14.0279445282,-3.81981860107,-1.18700709978>}
object {bead(material {texture {pigment {color rgb <0.043137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-13.5754301886,-1.19301659436,-3.81794596682>}
object {bead(material {texture {pigment {color rgb <0.0470588235294,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-13.122915849,2.46439726203,-3.15067391758>}
object {bead(material {texture {pigment {color rgb <0.0509803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-12.6704015094,3.99289100736,0.238372404784>}
object {bead(material {texture {pigment {color rgb <0.0549019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-12.2178871698,2.07204397561,3.42149583708>}
object {bead(material {texture {pigment {color rgb <0.0588235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-11.7653728301,-1.63878073492,3.64888992748>}
object {bead(material {texture {pigment {color rgb <0.0627450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-11.3128584905,-3.93391110187,0.724115627929>}
object {bead(material {texture {pigment {color rgb <0.0666666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-10.8603441509,-2.83065169257,-2.82620080591>}
object {bead(material {texture {pigment {color rgb <0.0705882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-10.4078298113,0.717924228217,-3.93504571797>}
object {bead(material {texture {pigment {color rgb <0.0745098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-9.95531547165,3.64630658232,-1.6445206924>}
object {bead(material {texture {pigment {color rgb <0.078431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-9.50280113203,3.42475222216,2.06665725673>}
object {bead(material {texture {pigment {color rgb <0.0823529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-9.05028679241,0.244655425079,3.99251095465>}
object {bead(material {texture {pigment {color rgb <0.0862745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-8.59777245279,-3.14679197799,2.46935219182>}
object {bead(material {texture {pigment {color rgb <0.0901960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-8.14525811317,-3.81981860107,-1.18700709978>}
object {bead(material {texture {pigment {color rgb <0.0941176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-7.69274377355,-1.19301659436,-3.81794596682>}
object {bead(material {texture {pigment {color rgb <0.0980392156863,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-7.24022943393,2.46439726203,-3.15067391758>}
object {bead(material {texture {pigment {color rgb <0.101960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-6.78771509431,3.99289100736,0.238372404784>}
object {bead(material {texture {pigment {color rgb <0.105882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-6.33520075469,2.07204397561,3.42149583708>}
object {bead(material {texture {pigment {color rgb <0.109803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.88268641507,-1.63878073492,3.64888992748>}
object {bead(material {texture {pigment {color rgb <0.113725490196,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.43017207545,-3.93391110187,0.724115627929>}
object {bead(material {texture {pigment {color rgb <0.117647058824,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.97765773583,-2.83065169257,-2.82620080591>}
object {bead(material {texture {pigment {color rgb <0.121568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.52514339621,0.717924228217,-3.93504571797>}
object {bead(material {texture {pigment {color rgb <0.125490196078,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.07262905659,3.64630658232,-1.6445206924>}
object {bead(material {texture {pigment {color rgb <0.129411764706,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.62011471696,3.42475222216,2.06665725673>}
object {bead(material {texture {pigment {color rgb <0.133333333333,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.16760037734,0.244655425079,3.99251095465>}
object {bead(material {texture {pigment {color rgb <0.137254901961,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.71508603772,-3.14679197799,2.46935219182>}
object {bead(material {texture {pigment {color rgb <0.141176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.2625716981,-3.81981860107,-1.18700709978>}
object {bead(material {texture {pigment {color rgb <0.145098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.81005735848,-1.19301659436,-3.81794596682>}
object {bead(material {texture {pigment {color rgb <0.149019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.35754301886,2.46439726203,-3.15067391758>}
object {bead(material {texture {pigment {color rgb <0.152941176471,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.905028679241,3.99289100736,0.238372404784>}
object {bead(material {texture {pigment {color rgb <0.156862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.452514339621,2.07204397561,3.42149583708>}
object {bead(material {texture {pigment {color rgb <0.160784313725,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0,-1.63878073492,3.64888992748>}
object {bead(material {texture {pigment {color rgb <0.164705882353,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.452514339621,-3.93391110187,0.724115627929>}
object {bead(material {texture {pigment {color rgb <0.16862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.905028679241,-2.83065169257,-2.82620080591>}
object {bead(material {texture {pigment {color rgb <0.172549019608,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.35754301886,0.717924228217,-3.93504571797>}
object {bead(material {texture {pigment {color rgb <0.176470588235,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.81005735848,3.64630658232,-1.6445206924>}
object {bead(material {texture {pigment {color rgb <0.180392156863,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.2625716981,3.42475222216,2.06665725673>}
object {bead(material {texture {pigment {color rgb <0.18431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.71508603772,0.244655425079,3.99251095465>}
object {bead(material {texture {pigment {color rgb <0.188235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.16760037734,-3.14679197799,2.46935219182>}
object {bead(material {texture {pigment {color rgb <0.192156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.62011471696,-3.81981860107,-1.18700709978>}
object {bead(material {texture {pigment {color rgb <0.196078431373,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.07262905659,-1.19301659436,-3.81794596682>}
object {bead(material {texture {pigment {color rgb <0.2,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.52514339621,2.46439726203,-3.15067391758>}
object {bead(material {texture {pigment {color rgb <0.203921568627,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.97765773583,3.99289100736,0.238372404784>}
object {bead(material {texture {pigment {color rgb <0.207843137255,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.43017207545,2.07204397561,3.42149583708>}
object {bead(material {texture {pigment {color rgb <0.211764705882,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.88268641507,-1.63878073492,3.64888992748>}
object {bead(material {texture {pigment {color rgb <0.21568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <6.33520075469,-3.93391110187,0.724115627929>}
object {bead(material {texture {pigment {color rgb <0.219607843137,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <6.78771509431,-2.83065169257,-2.82620080591>}
object {bead(material {texture {pigment {color rgb <0.223529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <7.24022943393,0.717924228217,-3.93504571797>}
object {bead(material {texture {pigment {color rgb <0.227450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <7.69274377355,3.64630658232,-1.6445206924>}
object {bead(material {texture {pigment {color rgb <0.23137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <8.14525811317,3.42475222216,2.06665725673>}
object {bead(material {texture {pigment {color rgb <0.235294117647,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <8.59777245279,0.244655425079,3.99251095465>}
object {bead(material {texture {pigment {color rgb <0.239215686275,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <9.05028679241,-3.14679197799,2.46935219182>}
object {bead(material {texture {pigment {color rgb <0.243137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <9.50280113203,-3.81981860107,-1.18700709978>}
object {bead(material {texture {pigment {color rgb <0.247058823529,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <9.95531547165,-1.19301659436,-3.81794596682>}
object {bead(material {texture {pigment {color rgb <0.250980392157,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <10.4078298113,2.46439726203,-3.15067391758>}
object {bead(material {texture {pigment {color rgb <0.254901960784,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <10.8603441509,3.99289100736,0.238372404784>}
object {bead(material {texture {pigment {color rgb <0.258823529412,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <11.3128584905,2.07204397561,3.42149583708>}
object {bead(material {texture {pigment {color rgb <0.262745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <11.7653728301,-1.63878073492,3.64888992748>}
object {bead(material {texture {pigment {color rgb <0.266666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <12.2178871698,-3.93391110187,0.724115627929>}
object {bead(material {texture {pigment {color rgb <0.270588235294,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <12.6704015094,-2.83065169257,-2.82620080591>}
object {bead(material {texture {pigment {color rgb <0.274509803922,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <13.122915849,0.717924228217,-3.93504571797>}
object {bead(material {texture {pigment {color rgb <0.278431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <13.5754301886,3.64630658232,-1.6445206924>}
object {bead(material {texture {pigment {color rgb <0.282352941176,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <14.0279445282,3.42475222216,2.06665725673>}
object {bead(material {texture {pigment {color rgb <0.286274509804,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <14.4804588679,0.244655425079,3.99251095465>}
object {bead(material {texture {pigment {color rgb <0.290196078431,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <14.9329732075,-3.14679197799,2.46935219182>}
object {bead(material {texture {pigment {color rgb <0.294117647059,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <15.3854875471,-3.81981860107,-1.18700709978>}
object {bead(material {texture {pigment {color rgb <0.298039215686,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <15.8380018867,-1.19301659436,-3.81794596682>}
object {bead(material {texture {pigment {color rgb <0.301960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <16.2905162263,2.46439726203,-3.15067391758>}
object {bead(material {texture {pigment {color rgb <0.305882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <16.743030566,3.99289100736,0.238372404784>}
object {bead(material {texture {pigment {color rgb <0.309803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <17.1955449056,2.07204397561,3.42149583708>}
object {bead(material {texture {pigment {color rgb <0.313725490196,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <17.6480592452,-1.63878073492,3.64888992748>}
object {bead(material {texture {pigment {color rgb <0.317647058824,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <18.1005735848,-3.93391110187,0.724115627929>}