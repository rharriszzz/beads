// Instrumentation only, inserted into a generated copy of the case-1 scene.
// Camera, bead_index, chain_angle, t1 and t2 come from the original beads.pov.
// Python checks the original case-1 shape arguments before generating the copy.
#declare VisibilityCode = bead_index + 1;
#declare VisibilityRGB = <mod(VisibilityCode,256),
  mod(floor(VisibilityCode/256),256), floor(VisibilityCode/65536)> / 255;
#declare VisibilityMaterial = material { texture {
  pigment { color rgb VisibilityRGB }
  finish { ambient 0 emission 1 diffuse 0 }
} }
object { bead(VisibilityMaterial,0.8,0.7,1.0)
  rotate <0,0,chain_angle>
  translate t1+t2+<0,0,chain_minor+2*bead_radius>
}
