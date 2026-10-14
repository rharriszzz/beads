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


camera { orthographic location <0,-0,80> direction <-0,0,-1> right <26.49677922,-3.005295629,-0> up <-2.10370694,-18.54774546,-0> }
background {color rgb 0}
object { bead(material {texture {pigment {color rgb <0.003921568627,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-5.246538723,2.360579747,3.229189257> }
object { bead(material {texture {pigment {color rgb <0.007843137255,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.871785957,-1.316608522,3.777107623> }
object { bead(material {texture {pigment {color rgb <0.01176470588,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.497033191,-3.856417521,1.062094114> }
object { bead(material {texture {pigment {color rgb <0.01568627451,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-4.122280425,-3.064781162,-2.570431176> }
object { bead(material {texture {pigment {color rgb <0.01960784314,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.747527659,0.3744292514,-3.982436784> }
object { bead(material {texture {pigment {color rgb <0.02352941176,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-3.372774893,3.490181278,-1.95413271> }
object { bead(material {texture {pigment {color rgb <0.02745098039,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.998022127,3.590868636,1.762288978> }
object { bead(material {texture {pigment {color rgb <0.03137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.623269362,0.5895104865,3.956321194> }
object { bead(material {texture {pigment {color rgb <0.03529411765,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-2.248516596,-2.921108385,2.732604216> }
object { bead(material {texture {pigment {color rgb <0.03921568627,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.87376383,-3.908267877,-0.8517289498> }
object { bead(material {texture {pigment {color rgb <0.0431372549,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.499011064,-1.519190018,-3.700278596> }
object { bead(material {texture {pigment {color rgb <0.04705882353,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-1.124258298,2.182271291,-3.352266697> }
object { bead(material {texture {pigment {color rgb <0.05098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.7495055319,3.998532795,-0.1083304686> }
object { bead(material {texture {pigment {color rgb <0.05490196078,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <-0.3747527659,2.360579747,3.229189257> }
object { bead(material {texture {pigment {color rgb <0.05882352941,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0,-1.316608522,3.777107623> }
object { bead(material {texture {pigment {color rgb <0.06274509804,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.3747527659,-3.856417521,1.062094114> }
object { bead(material {texture {pigment {color rgb <0.06666666667,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <0.7495055319,-3.064781162,-2.570431176> }
object { bead(material {texture {pigment {color rgb <0.07058823529,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.124258298,0.3744292514,-3.982436784> }
object { bead(material {texture {pigment {color rgb <0.07450980392,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.499011064,3.490181278,-1.95413271> }
object { bead(material {texture {pigment {color rgb <0.07843137255,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <1.87376383,3.590868636,1.762288978> }
object { bead(material {texture {pigment {color rgb <0.08235294118,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.248516596,0.5895104865,3.956321194> }
object { bead(material {texture {pigment {color rgb <0.0862745098,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.623269362,-2.921108385,2.732604216> }
object { bead(material {texture {pigment {color rgb <0.09019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <2.998022127,-3.908267877,-0.8517289498> }
object { bead(material {texture {pigment {color rgb <0.09411764706,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.372774893,-1.519190018,-3.700278596> }
object { bead(material {texture {pigment {color rgb <0.09803921569,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <3.747527659,2.182271291,-3.352266697> }
object { bead(material {texture {pigment {color rgb <0.1019607843,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.122280425,3.998532795,-0.1083304686> }
object { bead(material {texture {pigment {color rgb <0.1058823529,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.497033191,2.360579747,3.229189257> }
object { bead(material {texture {pigment {color rgb <0.1098039216,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <4.871785957,-1.316608522,3.777107623> }
object { bead(material {texture {pigment {color rgb <0.1137254902,0,0>} finish {ambient 1 diffuse 0}}},.8,.7,1) rotate <0,0,-90> translate <5.246538723,-3.856417521,1.062094114> }