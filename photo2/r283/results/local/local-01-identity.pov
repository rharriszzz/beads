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


camera {orthographic location <59.1594819068,-2.7188771401,80.7118565029> direction <-0.621175767507,0,-0.783671274108> right <-19.7230423899,-7.82345195462,15.6334376401> up <-4.81722572665,19.774459873,3.81836617836> }
background {color rgb 0}
object {bead(material {texture {pigment {color rgb <0.00392156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-26.8623022465,0.908655708809,-3.8954261388>}
object {bead(material {texture {pigment {color rgb <0.0078431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-26.4425787739,3.7220481381,-1.46504527495>}
object {bead(material {texture {pigment {color rgb <0.0117647058824,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-26.0228553013,3.32007295698,2.23094499268>}
object {bead(material {texture {pigment {color rgb <0.0156862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-25.6031318287,0.0499846687649,3.99968767942>}
object {bead(material {texture {pigment {color rgb <0.0196078431373,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-25.1834083561,-3.26328390057,2.31321814455>}
object {bead(material {texture {pigment {color rgb <0.0235294117647,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-24.7636848835,-3.75749775375,-1.37157232059>}
object {bead(material {texture {pigment {color rgb <0.0274509803922,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-24.3439614109,-1.00572011908,-3.87150191038>}
object {bead(material {texture {pigment {color rgb <0.0313725490196,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-23.9242379383,2.61486946429,-3.02695518379>}
object {bead(material {texture {pigment {color rgb <0.0352941176471,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-23.5045144657,3.97655043902,0.432488850683>}
object {bead(material {texture {pigment {color rgb <0.0392156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-23.0847909931,1.90300677171,3.51831852265>}
object {bead(material {texture {pigment {color rgb <0.043137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-22.6650675205,-1.81448831942,3.56477659029>}
object {bead(material {texture {pigment {color rgb <0.0470588235294,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-22.2453440479,-3.96450046694,0.531729299187>}
object {bead(material {texture {pigment {color rgb <0.0509803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-21.8256205753,-2.68969758792,-2.96066325095>}
object {bead(material {texture {pigment {color rgb <0.0549019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-21.4058971027,0.908655708809,-3.8954261388>}
object {bead(material {texture {pigment {color rgb <0.0588235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-20.9861736301,3.7220481381,-1.46504527495>}
object {bead(material {texture {pigment {color rgb <0.0627450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-20.5664501575,3.32007295698,2.23094499268>}
object {bead(material {texture {pigment {color rgb <0.0666666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-20.1467266849,0.0499846687649,3.99968767942>}
object {bead(material {texture {pigment {color rgb <0.0705882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-19.7270032123,-3.26328390057,2.31321814455>}
object {bead(material {texture {pigment {color rgb <0.0745098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-19.3072797397,-3.75749775375,-1.37157232058>}
object {bead(material {texture {pigment {color rgb <0.078431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-18.8875562671,-1.00572011908,-3.87150191038>}
object {bead(material {texture {pigment {color rgb <0.0823529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-18.4678327945,2.61486946429,-3.02695518379>}
object {bead(material {texture {pigment {color rgb <0.0862745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-18.0481093219,3.97655043902,0.432488850683>}
object {bead(material {texture {pigment {color rgb <0.0901960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-17.6283858493,1.90300677171,3.51831852265>}
object {bead(material {texture {pigment {color rgb <0.0941176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-17.2086623766,-1.81448831942,3.56477659029>}
object {bead(material {texture {pigment {color rgb <0.0980392156863,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-16.788938904,-3.96450046694,0.531729299187>}
object {bead(material {texture {pigment {color rgb <0.101960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-16.3692154314,-2.68969758792,-2.96066325095>}
object {bead(material {texture {pigment {color rgb <0.105882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-15.9494919588,0.908655708809,-3.8954261388>}
object {bead(material {texture {pigment {color rgb <0.109803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-15.5297684862,3.7220481381,-1.46504527495>}
object {bead(material {texture {pigment {color rgb <0.113725490196,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-15.1100450136,3.32007295698,2.23094499268>}
object {bead(material {texture {pigment {color rgb <0.117647058824,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-14.690321541,0.0499846687649,3.99968767942>}
object {bead(material {texture {pigment {color rgb <0.121568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-14.2705980684,-3.26328390057,2.31321814455>}
object {bead(material {texture {pigment {color rgb <0.125490196078,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-13.8508745958,-3.75749775375,-1.37157232058>}
object {bead(material {texture {pigment {color rgb <0.129411764706,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-13.4311511232,-1.00572011908,-3.87150191038>}
object {bead(material {texture {pigment {color rgb <0.133333333333,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-13.0114276506,2.61486946429,-3.02695518379>}
object {bead(material {texture {pigment {color rgb <0.137254901961,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-12.591704178,3.97655043902,0.432488850683>}
object {bead(material {texture {pigment {color rgb <0.141176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-12.1719807054,1.90300677171,3.51831852265>}
object {bead(material {texture {pigment {color rgb <0.145098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-11.7522572328,-1.81448831942,3.56477659029>}
object {bead(material {texture {pigment {color rgb <0.149019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-11.3325337602,-3.96450046694,0.531729299187>}
object {bead(material {texture {pigment {color rgb <0.152941176471,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-10.9128102876,-2.68969758792,-2.96066325095>}
object {bead(material {texture {pigment {color rgb <0.156862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-10.493086815,0.908655708809,-3.8954261388>}
object {bead(material {texture {pigment {color rgb <0.160784313725,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-10.0733633424,3.7220481381,-1.46504527495>}
object {bead(material {texture {pigment {color rgb <0.164705882353,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-9.65363986983,3.32007295698,2.23094499268>}
object {bead(material {texture {pigment {color rgb <0.16862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-9.23391639723,0.0499846687649,3.99968767942>}
object {bead(material {texture {pigment {color rgb <0.172549019608,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-8.81419292463,-3.26328390057,2.31321814455>}
object {bead(material {texture {pigment {color rgb <0.176470588235,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-8.39446945202,-3.75749775375,-1.37157232058>}
object {bead(material {texture {pigment {color rgb <0.180392156863,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-7.97474597942,-1.00572011908,-3.87150191038>}
object {bead(material {texture {pigment {color rgb <0.18431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-7.55502250682,2.61486946429,-3.02695518379>}
object {bead(material {texture {pigment {color rgb <0.188235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-7.13529903422,3.97655043902,0.432488850683>}
object {bead(material {texture {pigment {color rgb <0.192156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-6.71557556162,1.90300677171,3.51831852265>}
object {bead(material {texture {pigment {color rgb <0.196078431373,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-6.29585208902,-1.81448831942,3.56477659029>}
object {bead(material {texture {pigment {color rgb <0.2,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.87612861642,-3.96450046694,0.531729299187>}
object {bead(material {texture {pigment {color rgb <0.203921568627,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.45640514382,-2.68969758792,-2.96066325095>}
object {bead(material {texture {pigment {color rgb <0.207843137255,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.03668167121,0.908655708809,-3.8954261388>}
object {bead(material {texture {pigment {color rgb <0.211764705882,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.61695819861,3.7220481381,-1.46504527495>}
object {bead(material {texture {pigment {color rgb <0.21568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.19723472601,3.32007295698,2.23094499268>}
object {bead(material {texture {pigment {color rgb <0.219607843137,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.77751125341,0.0499846687649,3.99968767942>}
object {bead(material {texture {pigment {color rgb <0.223529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.35778778081,-3.26328390057,2.31321814455>}
object {bead(material {texture {pigment {color rgb <0.227450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.93806430821,-3.75749775375,-1.37157232058>}
object {bead(material {texture {pigment {color rgb <0.23137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.51834083561,-1.00572011908,-3.87150191038>}
object {bead(material {texture {pigment {color rgb <0.235294117647,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.09861736301,2.61486946429,-3.02695518379>}
object {bead(material {texture {pigment {color rgb <0.239215686275,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.6788938904,3.97655043902,0.432488850683>}
object {bead(material {texture {pigment {color rgb <0.243137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.2591704178,1.90300677171,3.51831852265>}
object {bead(material {texture {pigment {color rgb <0.247058823529,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.839446945202,-1.81448831942,3.56477659029>}
object {bead(material {texture {pigment {color rgb <0.250980392157,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.419723472601,-3.96450046694,0.531729299187>}
object {bead(material {texture {pigment {color rgb <0.254901960784,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0,-2.68969758792,-2.96066325095>}
object {bead(material {texture {pigment {color rgb <0.258823529412,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.419723472601,0.908655708809,-3.8954261388>}
object {bead(material {texture {pigment {color rgb <0.262745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.839446945202,3.7220481381,-1.46504527495>}
object {bead(material {texture {pigment {color rgb <0.266666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.2591704178,3.32007295698,2.23094499268>}
object {bead(material {texture {pigment {color rgb <0.270588235294,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.6788938904,0.0499846687649,3.99968767942>}
object {bead(material {texture {pigment {color rgb <0.274509803922,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.09861736301,-3.26328390057,2.31321814455>}
object {bead(material {texture {pigment {color rgb <0.278431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.51834083561,-3.75749775375,-1.37157232058>}
object {bead(material {texture {pigment {color rgb <0.282352941176,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.93806430821,-1.00572011908,-3.87150191038>}
object {bead(material {texture {pigment {color rgb <0.286274509804,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.35778778081,2.61486946429,-3.02695518379>}
object {bead(material {texture {pigment {color rgb <0.290196078431,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.77751125341,3.97655043902,0.432488850683>}
object {bead(material {texture {pigment {color rgb <0.294117647059,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.19723472601,1.90300677171,3.51831852265>}
object {bead(material {texture {pigment {color rgb <0.298039215686,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.61695819861,-1.81448831942,3.56477659029>}
object {bead(material {texture {pigment {color rgb <0.301960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.03668167121,-3.96450046694,0.531729299187>}
object {bead(material {texture {pigment {color rgb <0.305882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.45640514382,-2.68969758792,-2.96066325095>}
object {bead(material {texture {pigment {color rgb <0.309803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.87612861642,0.908655708809,-3.8954261388>}
object {bead(material {texture {pigment {color rgb <0.313725490196,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <6.29585208902,3.7220481381,-1.46504527495>}
object {bead(material {texture {pigment {color rgb <0.317647058824,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <6.71557556162,3.32007295698,2.23094499268>}
object {bead(material {texture {pigment {color rgb <0.321568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <7.13529903422,0.0499846687649,3.99968767942>}
object {bead(material {texture {pigment {color rgb <0.325490196078,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <7.55502250682,-3.26328390057,2.31321814455>}
object {bead(material {texture {pigment {color rgb <0.329411764706,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <7.97474597942,-3.75749775375,-1.37157232058>}
object {bead(material {texture {pigment {color rgb <0.333333333333,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <8.39446945202,-1.00572011908,-3.87150191038>}
object {bead(material {texture {pigment {color rgb <0.337254901961,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <8.81419292463,2.61486946429,-3.02695518379>}
object {bead(material {texture {pigment {color rgb <0.341176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <9.23391639723,3.97655043902,0.432488850683>}
object {bead(material {texture {pigment {color rgb <0.345098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <9.65363986983,1.90300677171,3.51831852265>}
object {bead(material {texture {pigment {color rgb <0.349019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <10.0733633424,-1.81448831942,3.56477659029>}
object {bead(material {texture {pigment {color rgb <0.352941176471,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <10.493086815,-3.96450046694,0.531729299187>}
object {bead(material {texture {pigment {color rgb <0.356862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <10.9128102876,-2.68969758792,-2.96066325095>}
object {bead(material {texture {pigment {color rgb <0.360784313725,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <11.3325337602,0.908655708809,-3.8954261388>}
object {bead(material {texture {pigment {color rgb <0.364705882353,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <11.7522572328,3.7220481381,-1.46504527495>}
object {bead(material {texture {pigment {color rgb <0.36862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <12.1719807054,3.32007295698,2.23094499268>}
object {bead(material {texture {pigment {color rgb <0.372549019608,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <12.591704178,0.0499846687649,3.99968767942>}
object {bead(material {texture {pigment {color rgb <0.376470588235,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <13.0114276506,-3.26328390057,2.31321814455>}
object {bead(material {texture {pigment {color rgb <0.380392156863,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <13.4311511232,-3.75749775375,-1.37157232058>}
object {bead(material {texture {pigment {color rgb <0.38431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <13.8508745958,-1.00572011908,-3.87150191038>}
object {bead(material {texture {pigment {color rgb <0.388235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <14.2705980684,2.61486946429,-3.02695518379>}
object {bead(material {texture {pigment {color rgb <0.392156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <14.690321541,3.97655043902,0.432488850683>}
object {bead(material {texture {pigment {color rgb <0.396078431373,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <15.1100450136,1.90300677171,3.51831852265>}
object {bead(material {texture {pigment {color rgb <0.4,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <15.5297684862,-1.81448831942,3.56477659029>}
object {bead(material {texture {pigment {color rgb <0.403921568627,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <15.9494919588,-3.96450046694,0.531729299187>}
object {bead(material {texture {pigment {color rgb <0.407843137255,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <16.3692154314,-2.68969758792,-2.96066325095>}
object {bead(material {texture {pigment {color rgb <0.411764705882,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <16.788938904,0.908655708809,-3.8954261388>}
object {bead(material {texture {pigment {color rgb <0.41568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <17.2086623766,3.7220481381,-1.46504527495>}
object {bead(material {texture {pigment {color rgb <0.419607843137,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <17.6283858493,3.32007295698,2.23094499268>}
object {bead(material {texture {pigment {color rgb <0.423529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <18.0481093219,0.049984668765,3.99968767942>}
object {bead(material {texture {pigment {color rgb <0.427450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <18.4678327945,-3.26328390057,2.31321814455>}
object {bead(material {texture {pigment {color rgb <0.43137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <18.8875562671,-3.75749775375,-1.37157232058>}
object {bead(material {texture {pigment {color rgb <0.435294117647,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <19.3072797397,-1.00572011908,-3.87150191038>}
object {bead(material {texture {pigment {color rgb <0.439215686275,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <19.7270032123,2.61486946429,-3.02695518379>}
object {bead(material {texture {pigment {color rgb <0.443137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <20.1467266849,3.97655043902,0.432488850683>}
object {bead(material {texture {pigment {color rgb <0.447058823529,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <20.5664501575,1.90300677171,3.51831852265>}
object {bead(material {texture {pigment {color rgb <0.450980392157,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <20.9861736301,-1.81448831942,3.56477659029>}
object {bead(material {texture {pigment {color rgb <0.454901960784,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <21.4058971027,-3.96450046694,0.531729299187>}
object {bead(material {texture {pigment {color rgb <0.458823529412,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <21.8256205753,-2.68969758792,-2.96066325095>}
object {bead(material {texture {pigment {color rgb <0.462745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <22.2453440479,0.908655708809,-3.8954261388>}
object {bead(material {texture {pigment {color rgb <0.466666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <22.6650675205,3.7220481381,-1.46504527495>}
object {bead(material {texture {pigment {color rgb <0.470588235294,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <23.0847909931,3.32007295698,2.23094499268>}
object {bead(material {texture {pigment {color rgb <0.474509803922,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <23.5045144657,0.049984668765,3.99968767942>}
object {bead(material {texture {pigment {color rgb <0.478431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <23.9242379383,-3.26328390057,2.31321814455>}
object {bead(material {texture {pigment {color rgb <0.482352941176,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <24.3439614109,-3.75749775375,-1.37157232058>}
object {bead(material {texture {pigment {color rgb <0.486274509804,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <24.7636848835,-1.00572011908,-3.87150191038>}
object {bead(material {texture {pigment {color rgb <0.490196078431,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <25.1834083561,2.61486946429,-3.02695518379>}
object {bead(material {texture {pigment {color rgb <0.494117647059,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <25.6031318287,3.97655043902,0.432488850683>}
object {bead(material {texture {pigment {color rgb <0.498039215686,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <26.0228553013,1.90300677171,3.51831852265>}
object {bead(material {texture {pigment {color rgb <0.501960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <26.4425787739,-1.81448831942,3.56477659029>}
object {bead(material {texture {pigment {color rgb <0.505882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <26.8623022465,-3.96450046694,0.531729299187>}