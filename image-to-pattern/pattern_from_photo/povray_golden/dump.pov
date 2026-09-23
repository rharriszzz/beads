// Ground-truth dump for pattern_from_photo/layout.py and pov_patterns.py.
//
// This includes the *real* beads.pov unmodified, then #debug-prints the
// derived geometry constants, the active color_pattern array, and the
// (chain_angle, row_angle, position) for a handful of bead_index samples,
// using formulas copy-pasted verbatim from beads.pov's bead-placement loop.
//
// Run via generate_golden.py, which sets `clock` (+K) to select
// bead_pattern 1-8 and parses the resulting #debug stream. Not needed at
// test time -- results are captured in golden_values.json.

#include "beads.pov"

// --- Named/custom color RGB dump (independent of bead_pattern) ---
// colors.inc named colors come from beads.pov's own #include. The three
// custom colors below are declared (verbatim) inside beads.pov's case
// 2/5/6 palette blocks, which only run for the matching bead_pattern, so we
// redeclare them here to dump them regardless of which case is active.
#declare MyBlue = color rgb <0.20, 0, 0.75>;
#declare Dark_Purple = color red 0.38 green 0.12 blue 0.37;
#declare Light_Purple = color red 0.87 green 0.58 blue 0.98;

#debug concat("COLOR Red ", str(Red.red,0,8), ",", str(Red.green,0,8), ",", str(Red.blue,0,8), "\n")
#debug concat("COLOR Green ", str(Green.red,0,8), ",", str(Green.green,0,8), ",", str(Green.blue,0,8), "\n")
#debug concat("COLOR Blue ", str(Blue.red,0,8), ",", str(Blue.green,0,8), ",", str(Blue.blue,0,8), "\n")
#debug concat("COLOR Yellow ", str(Yellow.red,0,8), ",", str(Yellow.green,0,8), ",", str(Yellow.blue,0,8), "\n")
#debug concat("COLOR White ", str(White.red,0,8), ",", str(White.green,0,8), ",", str(White.blue,0,8), "\n")
#debug concat("COLOR Black ", str(Black.red,0,8), ",", str(Black.green,0,8), ",", str(Black.blue,0,8), "\n")
#debug concat("COLOR Gray20 ", str(Gray20.red,0,8), ",", str(Gray20.green,0,8), ",", str(Gray20.blue,0,8), "\n")
#debug concat("COLOR LightBlue ", str(LightBlue.red,0,8), ",", str(LightBlue.green,0,8), ",", str(LightBlue.blue,0,8), "\n")
#debug concat("COLOR LimeGreen ", str(LimeGreen.red,0,8), ",", str(LimeGreen.green,0,8), ",", str(LimeGreen.blue,0,8), "\n")
#debug concat("COLOR OrangeRed ", str(OrangeRed.red,0,8), ",", str(OrangeRed.green,0,8), ",", str(OrangeRed.blue,0,8), "\n")
#debug concat("COLOR Plum ", str(Plum.red,0,8), ",", str(Plum.green,0,8), ",", str(Plum.blue,0,8), "\n")
#debug concat("COLOR SlateBlue ", str(SlateBlue.red,0,8), ",", str(SlateBlue.green,0,8), ",", str(SlateBlue.blue,0,8), "\n")
#debug concat("COLOR SteelBlue ", str(SteelBlue.red,0,8), ",", str(SteelBlue.green,0,8), ",", str(SteelBlue.blue,0,8), "\n")
#debug concat("COLOR MyBlue ", str(MyBlue.red,0,8), ",", str(MyBlue.green,0,8), ",", str(MyBlue.blue,0,8), "\n")
#debug concat("COLOR Dark_Purple ", str(Dark_Purple.red,0,8), ",", str(Dark_Purple.green,0,8), ",", str(Dark_Purple.blue,0,8), "\n")
#debug concat("COLOR Light_Purple ", str(Light_Purple.red,0,8), ",", str(Light_Purple.green,0,8), ",", str(Light_Purple.blue,0,8), "\n")

// --- Geometry / derived constants ---
#debug concat("BEAD_PATTERN=", str(bead_pattern,0,0), "\n")
#debug concat("CLOCK=", str(clock,0,8), "\n")
#debug concat("BCLOCK=", str(bclock,0,8), "\n")
#debug concat("RCLOCK=", str(rclock,0,8), "\n")
#debug concat("PATTERN_LENGTH=", str(pattern_length,0,0), "\n")
#debug concat("NGROUPS=", str(ngroups,0,0), "\n")
#debug concat("NBEADS=", str(nbeads,0,0), "\n")
#debug concat("NROWS=", str(nrows,0,0), "\n")
#debug concat("BEADS_PER_ROW=", str(beads_per_row,0,8), "\n")
#debug concat("EXACT_BEADS_PER_ROW=", str(exact_beads_per_row,0,8), "\n")
#debug concat("CHAIN_MINOR=", str(chain_minor,0,8), "\n")
#debug concat("BEAD_RADIUS=", str(bead_radius,0,8), "\n")
#debug concat("CHAIN_MAJOR=", str(chain_major,0,8), "\n")
#debug concat("HOLE_SIZE_PER_BEAD_SIZE=", str(hole_size_per_bead_size,0,8), "\n")

// --- color_pattern array dump ---
#declare _cpi = 0;
#while (_cpi < pattern_length)
  #debug concat("CP ", str(_cpi,0,0), " ", str(color_pattern[_cpi],0,0), "\n")
  #declare _cpi = _cpi + 1;
#end

// --- per-bead (chain_angle, row_angle, position) samples ---
// Formulas copied verbatim from beads.pov's bead-placement loop body.
#declare _nsamples = 11;
#declare _samples = array[_nsamples] {0, 1, 2, 3, 4, 5, 6, 7, floor(nbeads/2), floor(nbeads/2)+1, nbeads-1};
#declare _si = 0;
#while (_si < _nsamples)
  #declare bead_index = _samples[_si];
  #declare chain_angle = 360*(bead_index/nbeads + rclock*0.1666);
  #declare row_angle = 360*(bead_index/exact_beads_per_row + rclock*1.00);
  #declare t1 = vaxis_rotate(<chain_major, 0, 0>, z, chain_angle);
  #declare t2 = vaxis_rotate(<0, 0, chain_minor>, vcross(-z, t1), row_angle);
  #declare _pos = t1 + t2 + <0,0,chain_minor+2*bead_radius>;
  // POV-Ray's #debug stream wraps lines at ~80 columns, so each value gets
  // its own short, self-describing "NAME=value" line (a single combined
  // line was getting wrapped mid-number and silently dropping fields).
  #debug concat("BEAD", str(bead_index,0,0), "_CHAIN_ANGLE=", str(chain_angle,0,8), "\n")
  #debug concat("BEAD", str(bead_index,0,0), "_ROW_ANGLE=", str(row_angle,0,8), "\n")
  #debug concat("BEAD", str(bead_index,0,0), "_POS_X=", str(_pos.x,0,8), "\n")
  #debug concat("BEAD", str(bead_index,0,0), "_POS_Y=", str(_pos.y,0,8), "\n")
  #debug concat("BEAD", str(bead_index,0,0), "_POS_Z=", str(_pos.z,0,8), "\n")
  #declare _si = _si + 1;
#end
