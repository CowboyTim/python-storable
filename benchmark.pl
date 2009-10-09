#!/usr/bin/perl -w

use strict; use warnings;

use Data::Dumper;
use Storable qw(thaw nfreeze freeze);

use Benchmark;

my $small_data;
{
    open(my $fh, '<', "t/resources/x86_64-linux/2.18/050_complex06_2.18_x86_64-linux_nfreeze.storable");
    local $/;
    $small_data = <$fh>;
    close($fh);
}

#my $a = {a => 'x' x 100, b => 'y' x 50};
#my @data = map {{%{$a}}} 1..10_000;
#print freeze(\@data);

my $large_data;
{
    open(my $fh, '<', "t/large_simple01.storable");
    local $/;
    $large_data = <$fh>;
    close($fh);
}

timethese(1000, { 
    small_complex => sub { thaw($small_data) },
    large_simple  => sub { thaw($large_data) } 
});
