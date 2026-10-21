#version 3.7;
global_settings {assumed_gamma 1 max_trace_level 12 ambient_light rgb 1}
background {color rgb 1}
camera {orthographic location <0,0,200> direction <0,0,-1>
 right x*8 up y*9.180000000000001}
light_source {<-50,170,250> color rgb .85 parallel point_at <0,0,0>}
light_source {<120,20,180> color rgb .35 parallel point_at <0,0,0> shadowless}
#declare bead_radius=.95;
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


#declare BeadR=bead(material{texture{
 pigment{color rgb <0.66000000,0.02500000,0.04500000>} finish{ambient .20 diffuse .72 specular .13 roughness .055}
}},.8,.55,1);
#declare BeadY=bead(material{texture{
 pigment{color rgb <1.00000000,0.65000000,0.02500000>} finish{ambient .20 diffuse .72 specular .13 roughness .055}
}},.8,.55,1);
#declare BeadB=bead(material{texture{
 pigment{color rgb <0.01800000,0.02500000,0.03500000>} finish{ambient .20 diffuse .72 specular .13 roughness .055}
}},.8,.55,1);
intersection{ union{
cylinder{<0,-11.59,0>,<0,11.59,0>,1.85 texture {pigment {color rgb <0.60000000,0.53000000,0.40000000>} finish {ambient 1 diffuse 0}}}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.00392157>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.88545603,0.00000000,0.46472317,-0.46472317,0.00000000,0.88545603,0.00000000,-1.00000000,0.00000000,-1.16180793,8.84000000,2.21364006>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.00784314>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.88545603,0.00000000,-0.46472317,0.46472317,0.00000000,0.88545603,0.00000000,-1.00000000,0.00000000,1.16180793,8.50000000,2.21364006>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.01176471>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.12053668,0.00000000,-0.99270887,0.99270887,0.00000000,0.12053668,0.00000000,-1.00000000,0.00000000,2.48177219,8.16000000,0.30134170>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.01568627>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.74851075,0.00000000,-0.66312266,0.66312266,0.00000000,-0.74851075,0.00000000,-1.00000000,0.00000000,1.65780665,7.82000000,-1.87127687>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.01960784>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.97094182,0.00000000,0.23931566,-0.23931566,0.00000000,-0.97094182,0.00000000,-1.00000000,0.00000000,-0.59828916,7.48000000,-2.42735454>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.02352941>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.35460489,0.00000000,0.93501624,-0.93501624,0.00000000,-0.35460489,0.00000000,-1.00000000,0.00000000,-2.33754061,7.14000000,-0.88651222>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.02745098>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.56806475,0.00000000,0.82298387,-0.82298387,0.00000000,0.56806475,0.00000000,-1.00000000,0.00000000,-2.05745966,6.80000000,1.42016187>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.03137255>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <1.00000000,0.00000000,0.00000000,-0.00000000,0.00000000,1.00000000,0.00000000,-1.00000000,0.00000000,-0.00000000,6.46000000,2.50000000>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.03529412>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.56806475,0.00000000,-0.82298387,0.82298387,0.00000000,0.56806475,0.00000000,-1.00000000,0.00000000,2.05745966,6.12000000,1.42016187>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.03921569>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.35460489,0.00000000,-0.93501624,0.93501624,0.00000000,-0.35460489,0.00000000,-1.00000000,0.00000000,2.33754061,5.78000000,-0.88651222>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.04313725>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.97094182,0.00000000,-0.23931566,0.23931566,0.00000000,-0.97094182,0.00000000,-1.00000000,0.00000000,0.59828916,5.44000000,-2.42735454>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.04705882>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.74851075,0.00000000,0.66312266,-0.66312266,0.00000000,-0.74851075,0.00000000,-1.00000000,0.00000000,-1.65780665,5.10000000,-1.87127687>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.05098039>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.12053668,0.00000000,0.99270887,-0.99270887,0.00000000,0.12053668,0.00000000,-1.00000000,0.00000000,-2.48177219,4.76000000,0.30134170>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.05490196>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.88545603,0.00000000,0.46472317,-0.46472317,0.00000000,0.88545603,0.00000000,-1.00000000,0.00000000,-1.16180793,4.42000000,2.21364006>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.05882353>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.88545603,0.00000000,-0.46472317,0.46472317,0.00000000,0.88545603,0.00000000,-1.00000000,0.00000000,1.16180793,4.08000000,2.21364006>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.06274510>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.12053668,0.00000000,-0.99270887,0.99270887,0.00000000,0.12053668,0.00000000,-1.00000000,0.00000000,2.48177219,3.74000000,0.30134170>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.06666667>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.74851075,0.00000000,-0.66312266,0.66312266,0.00000000,-0.74851075,0.00000000,-1.00000000,0.00000000,1.65780665,3.40000000,-1.87127687>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.07058824>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.97094182,0.00000000,0.23931566,-0.23931566,0.00000000,-0.97094182,0.00000000,-1.00000000,0.00000000,-0.59828916,3.06000000,-2.42735454>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.07450980>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.35460489,0.00000000,0.93501624,-0.93501624,0.00000000,-0.35460489,0.00000000,-1.00000000,0.00000000,-2.33754061,2.72000000,-0.88651222>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.07843137>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.56806475,0.00000000,0.82298387,-0.82298387,0.00000000,0.56806475,0.00000000,-1.00000000,0.00000000,-2.05745966,2.38000000,1.42016187>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.08235294>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <1.00000000,0.00000000,0.00000000,-0.00000000,0.00000000,1.00000000,0.00000000,-1.00000000,0.00000000,-0.00000000,2.04000000,2.50000000>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.08627451>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.56806475,0.00000000,-0.82298387,0.82298387,0.00000000,0.56806475,0.00000000,-1.00000000,0.00000000,2.05745966,1.70000000,1.42016187>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.09019608>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.35460489,0.00000000,-0.93501624,0.93501624,0.00000000,-0.35460489,0.00000000,-1.00000000,0.00000000,2.33754061,1.36000000,-0.88651222>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.09411765>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.97094182,0.00000000,-0.23931566,0.23931566,0.00000000,-0.97094182,0.00000000,-1.00000000,0.00000000,0.59828916,1.02000000,-2.42735454>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.09803922>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.74851075,0.00000000,0.66312266,-0.66312266,0.00000000,-0.74851075,0.00000000,-1.00000000,0.00000000,-1.65780665,0.68000000,-1.87127687>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.10196078>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.12053668,0.00000000,0.99270887,-0.99270887,0.00000000,0.12053668,0.00000000,-1.00000000,0.00000000,-2.48177219,0.34000000,0.30134170>}
object{bead(material{texture {pigment {color rgb <1.00000000,0.00000000,0.00000000>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.88545603,0.00000000,0.46472317,-0.46472317,0.00000000,0.88545603,0.00000000,-1.00000000,0.00000000,-1.16180793,0.00000000,2.21364006>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.10980392>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.88545603,0.00000000,-0.46472317,0.46472317,0.00000000,0.88545603,0.00000000,-1.00000000,0.00000000,1.16180793,-0.34000000,2.21364006>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.11372549>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.12053668,0.00000000,-0.99270887,0.99270887,0.00000000,0.12053668,0.00000000,-1.00000000,0.00000000,2.48177219,-0.68000000,0.30134170>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.11764706>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.74851075,0.00000000,-0.66312266,0.66312266,0.00000000,-0.74851075,0.00000000,-1.00000000,0.00000000,1.65780665,-1.02000000,-1.87127687>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.12156863>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.97094182,0.00000000,0.23931566,-0.23931566,0.00000000,-0.97094182,0.00000000,-1.00000000,0.00000000,-0.59828916,-1.36000000,-2.42735454>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.12549020>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.35460489,0.00000000,0.93501624,-0.93501624,0.00000000,-0.35460489,0.00000000,-1.00000000,0.00000000,-2.33754061,-1.70000000,-0.88651222>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.12941176>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.56806475,0.00000000,0.82298387,-0.82298387,0.00000000,0.56806475,0.00000000,-1.00000000,0.00000000,-2.05745966,-2.04000000,1.42016187>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.13333333>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <1.00000000,0.00000000,0.00000000,-0.00000000,0.00000000,1.00000000,0.00000000,-1.00000000,0.00000000,-0.00000000,-2.38000000,2.50000000>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.13725490>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.56806475,0.00000000,-0.82298387,0.82298387,0.00000000,0.56806475,0.00000000,-1.00000000,0.00000000,2.05745966,-2.72000000,1.42016187>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.14117647>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.35460489,0.00000000,-0.93501624,0.93501624,0.00000000,-0.35460489,0.00000000,-1.00000000,0.00000000,2.33754061,-3.06000000,-0.88651222>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.14509804>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.97094182,0.00000000,-0.23931566,0.23931566,0.00000000,-0.97094182,0.00000000,-1.00000000,0.00000000,0.59828916,-3.40000000,-2.42735454>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.14901961>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.74851075,0.00000000,0.66312266,-0.66312266,0.00000000,-0.74851075,0.00000000,-1.00000000,0.00000000,-1.65780665,-3.74000000,-1.87127687>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.15294118>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.12053668,0.00000000,0.99270887,-0.99270887,0.00000000,0.12053668,0.00000000,-1.00000000,0.00000000,-2.48177219,-4.08000000,0.30134170>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.15686275>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.88545603,0.00000000,0.46472317,-0.46472317,0.00000000,0.88545603,0.00000000,-1.00000000,0.00000000,-1.16180793,-4.42000000,2.21364006>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.16078431>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.88545603,0.00000000,-0.46472317,0.46472317,0.00000000,0.88545603,0.00000000,-1.00000000,0.00000000,1.16180793,-4.76000000,2.21364006>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.16470588>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.12053668,0.00000000,-0.99270887,0.99270887,0.00000000,0.12053668,0.00000000,-1.00000000,0.00000000,2.48177219,-5.10000000,0.30134170>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.16862745>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.74851075,0.00000000,-0.66312266,0.66312266,0.00000000,-0.74851075,0.00000000,-1.00000000,0.00000000,1.65780665,-5.44000000,-1.87127687>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.17254902>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.97094182,0.00000000,0.23931566,-0.23931566,0.00000000,-0.97094182,0.00000000,-1.00000000,0.00000000,-0.59828916,-5.78000000,-2.42735454>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.17647059>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.35460489,0.00000000,0.93501624,-0.93501624,0.00000000,-0.35460489,0.00000000,-1.00000000,0.00000000,-2.33754061,-6.12000000,-0.88651222>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.18039216>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.56806475,0.00000000,0.82298387,-0.82298387,0.00000000,0.56806475,0.00000000,-1.00000000,0.00000000,-2.05745966,-6.46000000,1.42016187>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.18431373>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <1.00000000,0.00000000,-0.00000000,0.00000000,0.00000000,1.00000000,0.00000000,-1.00000000,0.00000000,0.00000000,-6.80000000,2.50000000>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.18823529>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.56806475,0.00000000,-0.82298387,0.82298387,0.00000000,0.56806475,0.00000000,-1.00000000,0.00000000,2.05745966,-7.14000000,1.42016187>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.19215686>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.35460489,0.00000000,-0.93501624,0.93501624,0.00000000,-0.35460489,0.00000000,-1.00000000,0.00000000,2.33754061,-7.48000000,-0.88651222>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.19607843>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.97094182,0.00000000,-0.23931566,0.23931566,0.00000000,-0.97094182,0.00000000,-1.00000000,0.00000000,0.59828916,-7.82000000,-2.42735454>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.20000000>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <-0.74851075,0.00000000,0.66312266,-0.66312266,0.00000000,-0.74851075,0.00000000,-1.00000000,0.00000000,-1.65780665,-8.16000000,-1.87127687>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.20392157>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.12053668,0.00000000,0.99270887,-0.99270887,0.00000000,0.12053668,0.00000000,-1.00000000,0.00000000,-2.48177219,-8.50000000,0.30134170>}
object{bead(material{texture {pigment {color rgb <0.00000000,0.00000000,0.20784314>} finish {ambient 1 diffuse 0}}},.8,.55,1) matrix <0.88545603,0.00000000,0.46472317,-0.46472317,0.00000000,0.88545603,0.00000000,-1.00000000,0.00000000,-1.16180793,-8.84000000,2.21364006>}
} box{<-5,-4.590000000000001,-6>,<5,4.590000000000001,6>} }
