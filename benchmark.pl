#!/usr/bin/perl -w

use strict; use warnings;

use Data::Dumper;
use Storable qw(thaw nfreeze freeze);

use Benchmark;

my $small_data_nfreeze;
{
    open(my $fh, '<', "t/resources/x86_64-linux/2.18/050_complex06_2.18_x86_64-linux_nfreeze.storable");
    local $/;
    $small_data_nfreeze = <$fh>;
    close($fh);
}

my $small_data_freeze;
{
    open(my $fh, '<', "t/resources/x86_64-linux/2.18/049_complex06_2.18_x86_64-linux_freeze.storable");
    local $/;
    $small_data_freeze = <$fh>;
    close($fh);
}

my $large_data_nfreeze;
{
    open(my $fh, '<', "t/large_simple01_nfreeze.storable");
    local $/;
    $large_data_nfreeze = <$fh>;
    close($fh);
}

my $large_data_freeze;
{
    open(my $fh, '<', "t/large_simple01_freeze.storable");
    local $/;
    $large_data_freeze = <$fh>;
    close($fh);
}

timethese(500, { 
    small_nfreeze => sub { thaw($small_data_nfreeze) },
    small_freeze  => sub { thaw($small_data_freeze)  },
    large_nfreeze => sub { thaw($large_data_nfreeze) },
    large_freeze  => sub { thaw($large_data_freeze)  } 
});

#my $a = {a => 'x' x 100, b => 'y' x 50};
#my @data = map {{%{$a}}} 1..10_000;
#print freeze(\@data);

