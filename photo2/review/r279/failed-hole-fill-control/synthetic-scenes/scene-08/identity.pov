#version 3.7;
global_settings { assumed_gamma 1.0 }
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


camera { orthographic location <40,-0,69.2820323> direction <-0.5,0,-0.8660254038> right <20.63018244,11.98492976,-11.91084138> up <7.265477541,-16.67517794,-4.194725414> }
background {color rgb 0}
object { bead(material {texture {pigment {color rgb <0.003921568627,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.246538723,-3.556589209,1.830484416> }
object { bead(material {texture {pigment {color rgb <0.007843137255,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.871785957,-3.526832089,-1.887181871> }
object { bead(material {texture {pigment {color rgb <0.01176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.497033191,-0.4503487459,-3.974567399> }
object { bead(material {texture {pigment {color rgb <0.01568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.122280425,3.015177597,-2.628441375> }
object { bead(material {texture {pigment {color rgb <0.01960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.747527659,3.875980942,0.9883176311> }
object { bead(material {texture {pigment {color rgb <0.02352941176,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.372774893,1.388438667,3.751298184> }
object { bead(material {texture {pigment {color rgb <0.02745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.998022127,-2.298534822,3.273642875> }
object { bead(material {texture {pigment {color rgb <0.03137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.623269362,-3.99987187,-0.03201596316> }
object { bead(material {texture {pigment {color rgb <0.03529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.248516596,-2.24583758,-3.310017155> }
object { bead(material {texture {pigment {color rgb <0.03921568627,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.87376383,1.448309558,-3.72859215> }
object { bead(material {texture {pigment {color rgb <0.0431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.499011064,3.891304785,-0.9261463562> }
object { bead(material {texture {pigment {color rgb <0.04705882353,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.124258298,2.972716576,2.67636996> }
object { bead(material {texture {pigment {color rgb <0.05098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.7495055319,-0.5139138074,3.966849203> }
object { bead(material {texture {pigment {color rgb <0.05490196078,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.3747527659,-3.556589209,1.830484416> }
object { bead(material {texture {pigment {color rgb <0.05882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0,-3.526832089,-1.887181871> }
object { bead(material {texture {pigment {color rgb <0.06274509804,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.3747527659,-0.4503487459,-3.974567399> }
object { bead(material {texture {pigment {color rgb <0.06666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.7495055319,3.015177597,-2.628441375> }
object { bead(material {texture {pigment {color rgb <0.07058823529,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.124258298,3.875980942,0.9883176311> }
object { bead(material {texture {pigment {color rgb <0.07450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.499011064,1.388438667,3.751298184> }
object { bead(material {texture {pigment {color rgb <0.07843137255,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.87376383,-2.298534822,3.273642875> }
object { bead(material {texture {pigment {color rgb <0.08235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.248516596,-3.99987187,-0.03201596316> }
object { bead(material {texture {pigment {color rgb <0.0862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.623269362,-2.24583758,-3.310017155> }
object { bead(material {texture {pigment {color rgb <0.09019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.998022127,1.448309558,-3.72859215> }
object { bead(material {texture {pigment {color rgb <0.09411764706,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.372774893,3.891304785,-0.9261463562> }
object { bead(material {texture {pigment {color rgb <0.09803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.747527659,2.972716576,2.67636996> }
object { bead(material {texture {pigment {color rgb <0.1019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.122280425,-0.5139138074,3.966849203> }
object { bead(material {texture {pigment {color rgb <0.1058823529,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.497033191,-3.556589209,1.830484416> }
object { bead(material {texture {pigment {color rgb <0.1098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.871785957,-3.526832089,-1.887181871> }
object { bead(material {texture {pigment {color rgb <0.1137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.246538723,-0.4503487459,-3.974567399> }