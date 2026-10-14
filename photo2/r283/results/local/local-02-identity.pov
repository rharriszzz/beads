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


camera {orthographic location <30.0094677247,2.42785793057,95.5127214599> direction <-0.25345274914,0,-0.967347767844> right <21.88784277,11.5779938407,-5.73478753682> up <8.79995796264,-17.7780849034,-2.30565843235> }
background {color rgb 0}
object {bead(material {texture {pigment {color rgb <0.00392156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-28.7809884397,3.78435940101,1.2956171981>}
object {bead(material {texture {pigment {color rgb <0.0078431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-28.3312854953,3.21603321508,-2.37847227427>}
object {bead(material {texture {pigment {color rgb <0.0117647058824,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-27.881582551,-0.130529213395,-3.99786969828>}
object {bead(material {texture {pigment {color rgb <0.0156862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-27.4318796066,-3.36433130418,-2.16362540097>}
object {bead(material {texture {pigment {color rgb <0.0196078431373,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-26.9821766622,-3.69178680706,1.53971106744>}
object {bead(material {texture {pigment {color rgb <0.0235294117647,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-26.5324737179,-0.830016570899,3.9129365561>}
object {bead(material {texture {pigment {color rgb <0.0274509803922,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-26.0827707735,2.7487805008,2.90589155999>}
object {bead(material {texture {pigment {color rgb <0.0313725490196,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-25.6330678291,3.95298716891,-0.611467449991>}
object {bead(material {texture {pigment {color rgb <0.0352941176471,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-25.1833648848,1.74232480908,-3.60059776421>}
object {bead(material {texture {pigment {color rgb <0.0392156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-24.7336619404,-1.97348056613,-3.47927786403>}
object {bead(material {texture {pigment {color rgb <0.043137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-24.283958996,-3.98445428503,-0.352312433058>}
object {bead(material {texture {pigment {color rgb <0.0470588235294,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-23.8342560516,-2.55337546245,3.07900531792>}
object {bead(material {texture {pigment {color rgb <0.0509803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-23.3845531073,1.08348911426,3.85046118527>}
object {bead(material {texture {pigment {color rgb <0.0549019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-22.9348501629,3.78435940101,1.2956171981>}
object {bead(material {texture {pigment {color rgb <0.0588235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-22.4851472185,3.21603321508,-2.37847227427>}
object {bead(material {texture {pigment {color rgb <0.0627450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-22.0354442742,-0.130529213395,-3.99786969828>}
object {bead(material {texture {pigment {color rgb <0.0666666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-21.5857413298,-3.36433130418,-2.16362540097>}
object {bead(material {texture {pigment {color rgb <0.0705882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-21.1360383854,-3.69178680706,1.53971106744>}
object {bead(material {texture {pigment {color rgb <0.0745098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-20.686335441,-0.830016570899,3.9129365561>}
object {bead(material {texture {pigment {color rgb <0.078431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-20.2366324967,2.7487805008,2.90589155999>}
object {bead(material {texture {pigment {color rgb <0.0823529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-19.7869295523,3.95298716891,-0.611467449991>}
object {bead(material {texture {pigment {color rgb <0.0862745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-19.3372266079,1.74232480908,-3.60059776421>}
object {bead(material {texture {pigment {color rgb <0.0901960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-18.8875236636,-1.97348056613,-3.47927786403>}
object {bead(material {texture {pigment {color rgb <0.0941176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-18.4378207192,-3.98445428503,-0.352312433058>}
object {bead(material {texture {pigment {color rgb <0.0980392156863,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-17.9881177748,-2.55337546245,3.07900531792>}
object {bead(material {texture {pigment {color rgb <0.101960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-17.5384148305,1.08348911426,3.85046118527>}
object {bead(material {texture {pigment {color rgb <0.105882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-17.0887118861,3.78435940101,1.2956171981>}
object {bead(material {texture {pigment {color rgb <0.109803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-16.6390089417,3.21603321508,-2.37847227427>}
object {bead(material {texture {pigment {color rgb <0.113725490196,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-16.1893059973,-0.130529213395,-3.99786969828>}
object {bead(material {texture {pigment {color rgb <0.117647058824,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-15.739603053,-3.36433130418,-2.16362540097>}
object {bead(material {texture {pigment {color rgb <0.121568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-15.2899001086,-3.69178680706,1.53971106744>}
object {bead(material {texture {pigment {color rgb <0.125490196078,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-14.8401971642,-0.830016570899,3.9129365561>}
object {bead(material {texture {pigment {color rgb <0.129411764706,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-14.3904942199,2.7487805008,2.90589155999>}
object {bead(material {texture {pigment {color rgb <0.133333333333,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-13.9407912755,3.95298716891,-0.611467449991>}
object {bead(material {texture {pigment {color rgb <0.137254901961,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-13.4910883311,1.74232480908,-3.60059776421>}
object {bead(material {texture {pigment {color rgb <0.141176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-13.0413853867,-1.97348056613,-3.47927786403>}
object {bead(material {texture {pigment {color rgb <0.145098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-12.5916824424,-3.98445428503,-0.352312433058>}
object {bead(material {texture {pigment {color rgb <0.149019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-12.141979498,-2.55337546245,3.07900531792>}
object {bead(material {texture {pigment {color rgb <0.152941176471,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-11.6922765536,1.08348911426,3.85046118527>}
object {bead(material {texture {pigment {color rgb <0.156862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-11.2425736093,3.78435940101,1.2956171981>}
object {bead(material {texture {pigment {color rgb <0.160784313725,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-10.7928706649,3.21603321508,-2.37847227427>}
object {bead(material {texture {pigment {color rgb <0.164705882353,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-10.3431677205,-0.130529213395,-3.99786969828>}
object {bead(material {texture {pigment {color rgb <0.16862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-9.89346477615,-3.36433130418,-2.16362540097>}
object {bead(material {texture {pigment {color rgb <0.172549019608,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-9.44376183178,-3.69178680706,1.53971106744>}
object {bead(material {texture {pigment {color rgb <0.176470588235,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-8.99405888741,-0.830016570899,3.9129365561>}
object {bead(material {texture {pigment {color rgb <0.180392156863,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-8.54435594304,2.7487805008,2.90589155999>}
object {bead(material {texture {pigment {color rgb <0.18431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-8.09465299867,3.95298716891,-0.611467449991>}
object {bead(material {texture {pigment {color rgb <0.188235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-7.6449500543,1.74232480908,-3.60059776421>}
object {bead(material {texture {pigment {color rgb <0.192156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-7.19524710993,-1.97348056613,-3.47927786403>}
object {bead(material {texture {pigment {color rgb <0.196078431373,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-6.74554416556,-3.98445428503,-0.352312433058>}
object {bead(material {texture {pigment {color rgb <0.2,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-6.29584122119,-2.55337546245,3.07900531792>}
object {bead(material {texture {pigment {color rgb <0.203921568627,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.84613827682,1.08348911426,3.85046118527>}
object {bead(material {texture {pigment {color rgb <0.207843137255,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.39643533245,3.78435940101,1.2956171981>}
object {bead(material {texture {pigment {color rgb <0.211764705882,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.94673238808,3.21603321508,-2.37847227427>}
object {bead(material {texture {pigment {color rgb <0.21568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.49702944371,-0.130529213395,-3.99786969828>}
object {bead(material {texture {pigment {color rgb <0.219607843137,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.04732649933,-3.36433130418,-2.16362540097>}
object {bead(material {texture {pigment {color rgb <0.223529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.59762355496,-3.69178680706,1.53971106744>}
object {bead(material {texture {pigment {color rgb <0.227450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.14792061059,-0.830016570899,3.9129365561>}
object {bead(material {texture {pigment {color rgb <0.23137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.69821766622,2.7487805008,2.90589155999>}
object {bead(material {texture {pigment {color rgb <0.235294117647,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.24851472185,3.95298716891,-0.611467449991>}
object {bead(material {texture {pigment {color rgb <0.239215686275,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.79881177748,1.74232480908,-3.60059776421>}
object {bead(material {texture {pigment {color rgb <0.243137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.34910883311,-1.97348056613,-3.47927786403>}
object {bead(material {texture {pigment {color rgb <0.247058823529,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.899405888741,-3.98445428503,-0.352312433058>}
object {bead(material {texture {pigment {color rgb <0.250980392157,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.449702944371,-2.55337546245,3.07900531792>}
object {bead(material {texture {pigment {color rgb <0.254901960784,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0,1.08348911426,3.85046118527>}
object {bead(material {texture {pigment {color rgb <0.258823529412,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.449702944371,3.78435940101,1.2956171981>}
object {bead(material {texture {pigment {color rgb <0.262745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.899405888741,3.21603321508,-2.37847227427>}
object {bead(material {texture {pigment {color rgb <0.266666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.34910883311,-0.130529213395,-3.99786969828>}
object {bead(material {texture {pigment {color rgb <0.270588235294,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.79881177748,-3.36433130418,-2.16362540097>}
object {bead(material {texture {pigment {color rgb <0.274509803922,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.24851472185,-3.69178680706,1.53971106744>}
object {bead(material {texture {pigment {color rgb <0.278431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.69821766622,-0.830016570899,3.9129365561>}
object {bead(material {texture {pigment {color rgb <0.282352941176,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.14792061059,2.7487805008,2.90589155999>}
object {bead(material {texture {pigment {color rgb <0.286274509804,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.59762355496,3.95298716891,-0.611467449991>}
object {bead(material {texture {pigment {color rgb <0.290196078431,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.04732649933,1.74232480908,-3.60059776421>}
object {bead(material {texture {pigment {color rgb <0.294117647059,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.49702944371,-1.97348056613,-3.47927786403>}
object {bead(material {texture {pigment {color rgb <0.298039215686,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.94673238808,-3.98445428503,-0.352312433058>}
object {bead(material {texture {pigment {color rgb <0.301960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.39643533245,-2.55337546245,3.07900531792>}
object {bead(material {texture {pigment {color rgb <0.305882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.84613827682,1.08348911426,3.85046118527>}
object {bead(material {texture {pigment {color rgb <0.309803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <6.29584122119,3.78435940101,1.2956171981>}
object {bead(material {texture {pigment {color rgb <0.313725490196,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <6.74554416556,3.21603321508,-2.37847227427>}
object {bead(material {texture {pigment {color rgb <0.317647058824,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <7.19524710993,-0.130529213395,-3.99786969828>}
object {bead(material {texture {pigment {color rgb <0.321568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <7.6449500543,-3.36433130418,-2.16362540097>}
object {bead(material {texture {pigment {color rgb <0.325490196078,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <8.09465299867,-3.69178680706,1.53971106744>}
object {bead(material {texture {pigment {color rgb <0.329411764706,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <8.54435594304,-0.830016570899,3.9129365561>}
object {bead(material {texture {pigment {color rgb <0.333333333333,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <8.99405888741,2.7487805008,2.90589155999>}
object {bead(material {texture {pigment {color rgb <0.337254901961,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <9.44376183178,3.95298716891,-0.611467449991>}
object {bead(material {texture {pigment {color rgb <0.341176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <9.89346477615,1.74232480908,-3.60059776421>}
object {bead(material {texture {pigment {color rgb <0.345098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <10.3431677205,-1.97348056613,-3.47927786403>}
object {bead(material {texture {pigment {color rgb <0.349019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <10.7928706649,-3.98445428503,-0.352312433058>}
object {bead(material {texture {pigment {color rgb <0.352941176471,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <11.2425736093,-2.55337546245,3.07900531792>}
object {bead(material {texture {pigment {color rgb <0.356862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <11.6922765536,1.08348911426,3.85046118527>}
object {bead(material {texture {pigment {color rgb <0.360784313725,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <12.141979498,3.78435940101,1.2956171981>}
object {bead(material {texture {pigment {color rgb <0.364705882353,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <12.5916824424,3.21603321508,-2.37847227427>}
object {bead(material {texture {pigment {color rgb <0.36862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <13.0413853867,-0.130529213395,-3.99786969828>}
object {bead(material {texture {pigment {color rgb <0.372549019608,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <13.4910883311,-3.36433130418,-2.16362540097>}
object {bead(material {texture {pigment {color rgb <0.376470588235,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <13.9407912755,-3.69178680706,1.53971106744>}
object {bead(material {texture {pigment {color rgb <0.380392156863,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <14.3904942199,-0.830016570899,3.9129365561>}
object {bead(material {texture {pigment {color rgb <0.38431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <14.8401971642,2.7487805008,2.90589155999>}
object {bead(material {texture {pigment {color rgb <0.388235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <15.2899001086,3.95298716891,-0.611467449991>}
object {bead(material {texture {pigment {color rgb <0.392156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <15.739603053,1.74232480908,-3.60059776421>}
object {bead(material {texture {pigment {color rgb <0.396078431373,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <16.1893059973,-1.97348056613,-3.47927786403>}
object {bead(material {texture {pigment {color rgb <0.4,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <16.6390089417,-3.98445428503,-0.352312433058>}
object {bead(material {texture {pigment {color rgb <0.403921568627,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <17.0887118861,-2.55337546245,3.07900531792>}
object {bead(material {texture {pigment {color rgb <0.407843137255,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <17.5384148305,1.08348911426,3.85046118527>}
object {bead(material {texture {pigment {color rgb <0.411764705882,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <17.9881177748,3.78435940101,1.2956171981>}
object {bead(material {texture {pigment {color rgb <0.41568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <18.4378207192,3.21603321508,-2.37847227427>}
object {bead(material {texture {pigment {color rgb <0.419607843137,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <18.8875236636,-0.130529213395,-3.99786969828>}
object {bead(material {texture {pigment {color rgb <0.423529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <19.3372266079,-3.36433130418,-2.16362540097>}
object {bead(material {texture {pigment {color rgb <0.427450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <19.7869295523,-3.69178680706,1.53971106744>}
object {bead(material {texture {pigment {color rgb <0.43137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <20.2366324967,-0.830016570899,3.9129365561>}
object {bead(material {texture {pigment {color rgb <0.435294117647,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <20.686335441,2.7487805008,2.90589155999>}
object {bead(material {texture {pigment {color rgb <0.439215686275,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <21.1360383854,3.95298716891,-0.611467449991>}
object {bead(material {texture {pigment {color rgb <0.443137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <21.5857413298,1.74232480908,-3.60059776421>}
object {bead(material {texture {pigment {color rgb <0.447058823529,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <22.0354442742,-1.97348056613,-3.47927786403>}
object {bead(material {texture {pigment {color rgb <0.450980392157,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <22.4851472185,-3.98445428503,-0.352312433058>}
object {bead(material {texture {pigment {color rgb <0.454901960784,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <22.9348501629,-2.55337546245,3.07900531792>}
object {bead(material {texture {pigment {color rgb <0.458823529412,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <23.3845531073,1.08348911426,3.85046118527>}
object {bead(material {texture {pigment {color rgb <0.462745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <23.8342560516,3.78435940101,1.2956171981>}
object {bead(material {texture {pigment {color rgb <0.466666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <24.283958996,3.21603321508,-2.37847227427>}
object {bead(material {texture {pigment {color rgb <0.470588235294,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <24.7336619404,-0.130529213395,-3.99786969828>}
object {bead(material {texture {pigment {color rgb <0.474509803922,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <25.1833648848,-3.36433130418,-2.16362540097>}
object {bead(material {texture {pigment {color rgb <0.478431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <25.6330678291,-3.69178680706,1.53971106744>}
object {bead(material {texture {pigment {color rgb <0.482352941176,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <26.0827707735,-0.830016570899,3.9129365561>}
object {bead(material {texture {pigment {color rgb <0.486274509804,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <26.5324737179,2.7487805008,2.90589155999>}
object {bead(material {texture {pigment {color rgb <0.490196078431,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <26.9821766622,3.95298716891,-0.611467449991>}
object {bead(material {texture {pigment {color rgb <0.494117647059,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <27.4318796066,1.74232480908,-3.60059776421>}
object {bead(material {texture {pigment {color rgb <0.498039215686,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <27.881582551,-1.97348056613,-3.47927786403>}
object {bead(material {texture {pigment {color rgb <0.501960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <28.3312854953,-3.98445428503,-0.352312433058>}
object {bead(material {texture {pigment {color rgb <0.505882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <28.7809884397,-2.55337546245,3.07900531792>}