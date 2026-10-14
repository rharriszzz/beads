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


camera {orthographic location <41.5131767784,-0,68.3860815793> direction <-0.51891470973,0,-0.854826019741> right <29.4404690275,-1.42397762189,-17.8715809848> up <-0.852077185906,-24.108213652,0.517246054029> }
background {color rgb 0}
object {bead(material {texture {pigment {color rgb <0.00392156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-6.50570801665,-3.41677522534,2.07981899682>}
object {bead(material {texture {pigment {color rgb <0.0078431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-6.04101458689,-0.229292074655,3.99342273551>}
object {bead(material {texture {pigment {color rgb <0.0117647058824,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.57632115713,3.1562697367,2.45722635286>}
object {bead(material {texture {pigment {color rgb <0.0156862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.11162772737,3.81522321185,-1.20169540392>}
object {bead(material {texture {pigment {color rgb <0.0196078431373,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.64693429761,1.17831787842,-3.82250794341>}
object {bead(material {texture {pigment {color rgb <0.0235294117647,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.18224086785,-2.4765015175,-3.14116860958>}
object {bead(material {texture {pigment {color rgb <0.0274509803922,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.71754743809,-3.99194429306,0.253733642124>}
object {bead(material {texture {pigment {color rgb <0.0313725490196,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.25285400833,-2.0588641301,3.42944288388>}
object {bead(material {texture {pigment {color rgb <0.0352941176471,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.78816057856,1.65280803182,3.6425575644>}
object {bead(material {texture {pigment {color rgb <0.0392156862745,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.3234671488,3.93666808208,0.708974196666>}
object {bead(material {texture {pigment {color rgb <0.043137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.85877371904,2.8197566822,-2.83707106946>}
object {bead(material {texture {pigment {color rgb <0.0470588235294,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.39408028928,-0.733059351043,-3.93225431373>}
object {bead(material {texture {pigment {color rgb <0.0509803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.929386859522,-3.65260703138,-1.63047903216>}
object {bead(material {texture {pigment {color rgb <0.0549019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.464693429761,-3.41677522534,2.07981899682>}
object {bead(material {texture {pigment {color rgb <0.0588235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0,-0.229292074655,3.99342273551>}
object {bead(material {texture {pigment {color rgb <0.0627450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.464693429761,3.1562697367,2.45722635286>}
object {bead(material {texture {pigment {color rgb <0.0666666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.929386859522,3.81522321185,-1.20169540392>}
object {bead(material {texture {pigment {color rgb <0.0705882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.39408028928,1.17831787842,-3.82250794341>}
object {bead(material {texture {pigment {color rgb <0.0745098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.85877371904,-2.4765015175,-3.14116860958>}
object {bead(material {texture {pigment {color rgb <0.078431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.3234671488,-3.99194429306,0.253733642124>}
object {bead(material {texture {pigment {color rgb <0.0823529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.78816057856,-2.0588641301,3.42944288388>}
object {bead(material {texture {pigment {color rgb <0.0862745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.25285400833,1.65280803182,3.6425575644>}
object {bead(material {texture {pigment {color rgb <0.0901960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.71754743809,3.93666808208,0.708974196666>}
object {bead(material {texture {pigment {color rgb <0.0941176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.18224086785,2.8197566822,-2.83707106946>}
object {bead(material {texture {pigment {color rgb <0.0980392156863,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.64693429761,-0.733059351043,-3.93225431373>}
object {bead(material {texture {pigment {color rgb <0.101960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.11162772737,-3.65260703138,-1.63047903216>}
object {bead(material {texture {pigment {color rgb <0.105882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.57632115713,-3.41677522534,2.07981899682>}
object {bead(material {texture {pigment {color rgb <0.109803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <6.04101458689,-0.229292074655,3.99342273551>}
object {bead(material {texture {pigment {color rgb <0.113725490196,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <6.50570801665,3.1562697367,2.45722635286>}