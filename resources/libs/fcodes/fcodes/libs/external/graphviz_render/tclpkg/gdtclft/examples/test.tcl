#!/bin/sh
# next line is a comment in tcl \
exec tclsh "$0" ${1+"$@"}

package require Gdtclft

if 1 {
set font(1) /usr/add-on/share/ttf/blf.ttf
set font(2) /usr/add-on/share/ttf/atrox.ttf 
set font(3) /usr/add-on/share/ttf/barcod39.ttf 
set font(4) /usr/add-on/share/ttf/bkkoi8bi.ttf 
set font(5) /usr/add-on/share/ttf/bkmaci.ttf 
set font(6) /usr/add-on/share/ttf/times.ttf 
set font(7) /usr/add-on/share/ttf/verdana.ttf 
set font(8) /usr/add-on/share/ttf/arial.ttf 
set font(9) /usr/add-on/share/ttf/frzquadb.ttf 
} {
set font(1) /usr/add-on/share/ttf/times.ttf 
set font(2) /usr/add-on/share/ttf/times.ttf 
set font(3) /usr/add-on/share/ttf/times.ttf 
set font(4) /usr/add-on/share/ttf/times.ttf 
set font(5) /usr/add-on/share/ttf/times.ttf 
set font(6) /usr/add-on/share/ttf/times.ttf 
set font(7) /usr/add-on/share/ttf/times.ttf 
set font(8) /usr/add-on/share/ttf/times.ttf 
set font(9) /usr/add-on/share/ttf/times.ttf 
}

#set string "ABC,abc.GJQYZ?gjqyz!M"
set string "mmmmmmmmmmmmmmmmmmmmmm"

set gd [gd create 600 700]
set white [gd color new $gd 255 255 255]
set color.green [gd color new $gd 0 255 0]
set black [gd color new $gd 0 0 0]

set start [clock clicks]

set angle .5
set x 50
set f 6
if 1 {
	set y 40
	for {set i 4} {$i < 18} {set i [expr $i + .5]} {
		set y [expr $y + round($i) + 5]
		gd fillpolygon $gd $color.green [gd text {} $black $font($f) $i $angle $x $y "$i: $string"]
		gd text $gd $black $font($f) $i $angle $x $y "$i: $string"
	}

} {
	set y 250
	set i 15.5
if 0 {
	gd fillpolygon $gd $color.green [gd text {} $black $font($f) $i $angle $x $y "$i: $string"]
	gd text $gd $black $font($f) $i $angle $x $y "$i: $string"
}
}

if 1 {
for {set f 1} {$f <= 9} {incr f} {
	set y [expr $y + round($i) + 5]
	gd text $gd $black $font($f) $i 0.0 $x $y "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
}
}

puts [expr [clock clicks] - $start]
	
set f [open "| xv -" w]
#set f [open "test.png" w]
gd writePNG $gd $f
close $f
