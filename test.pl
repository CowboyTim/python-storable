#!/usr/bin/perl

use strict; use warnings;

use FindBin;
use Fatal qw(open);
use File::Path qw(mkpath);
use Config;

use Storable qw(nfreeze freeze);

# make the base path
my $base = $FindBin::Bin.'/resources';
mkpath($base);
my $filenames = {};
my $count     = 0;

# very simple tests: note, for storable. all a ref
save_sample('scalar',        \'Some scalar, less then 255 bytes size');
save_sample('empty_hash',    {});
save_sample('empty_array',   []);
save_sample('double',        \7.9);
save_sample('undef',         \undef);

# large scalars are different in storable, make one that is bigger than
# 255 bytes, (one byte size denomination)
my $lscalar = 'x' x 1024;
save_sample('large_scalar',  \$lscalar);

# more complex tests, still nothing fancy: just a hash, hash in hash,
# array in a hash, array in array, hash in array. All with multiple elements
# too of course, and combined as much as possible.
save_sample('simple_hash01', {aa => 'bb'});
save_sample('simple_hash02', {aa => {bb => 'cc'}});
save_sample('simple_hash03', {aa => {bb => 7.8}});
save_sample('simple_hash04', {aa => []});
save_sample('simple_hash05', {aa => ['bb', 6.77]});
save_sample('simple_hash06', {aa => 'bb', 0.667 => 'test', abc => 66.77});
save_sample('simple_hash07', {aa => undef, bb => undef, undef => undef});
save_sample('simple_hash08', [undef, {}, 8.9, 'aa', undef, undef]);
save_sample('simple_hash09', [
    [0.6, 0.7], {a => 'b'}, undef, ['uu','ii', [undef], [7,8,9,{}]]
]);


# In python, there are no refs, hence, this must all be the same: all just
# an array
my @array = ();
save_sample('ref01', \@array);
save_sample('ref02', \\@array);
save_sample('ref03', \\\@array);
save_sample('ref04', \\\\@array);

{
    # same object, added + shared multiple times in an array. In python,
    # that is preferrably also the same object. This is possible too. Note
    # that this is a circular test allready too
    $array[5] = 'x';
    my $a = [undef, \@array, \@array, \\@array, \\@array];
    save_sample('complex01', $a);
}

{
    # in perl, a scalar copy is a scalar copy, hence 2 different objects
    # in python
    my $a = {aa => 'bb'};
    $a->{cc} = $a->{aa};
    save_sample('complex02', $a);
}

{
    # .. but a ref must make it the same object. NOTE: in python, everything
    # is a ref, hence, no extra ref/deref is possible. This basically needs
    # to give the same result in python as the previous sample.
    my $a = {aa => 'bb'};
    $a->{cc} = \$a->{aa};
    save_sample('complex03', $a);
}

{
    # same thing with an array of course.
    my $a = [undef, 6, [qw(a b c), {'uu' => 5.6}]];
    $a->[6] = \$a->[0];
    $a->[7] = \$a->[1];
    $a->[5] =  $a->[2];
    $a->[4] =  $a->[2][3];
    $a->[3] =  $a->[2][3];
    save_sample('complex04', $a);

    # a small circular one: hash with ref to it's own
    $a->[2][3]{ii} = $a->[2][3];
    save_sample('complex05', $a);

    # a circular one over the entire structure.... niiiice.
    $a->[2][3]{oo} = $a;
    save_sample('complex06', $a);
}

{
    # small circular one with an array
    my $a = [undef, 'yy'];
    push @{$a}, $a;
    save_sample('complex07', $a);
}

sub save_sample {
    my ($what, $data) = @_;
    for my $type (qw(freeze nfreeze)){
        $count++;
        my $filename =
            "$base/".sprintf('%03d', $count)."_${what}_".
            "${Storable::VERSION}_$Config{myarchname}_${type}.storable";

        print "saving sample $what for $type to $filename\n";
        die "Duplicate filename $filename\n"
            if exists $filenames->{$filename};
        $filenames->{$filename} = 1;
        my $a;
        {
            no strict 'refs';
            $a = &$type($data);
        }
        open(my $fh, ">", $filename);
        print $fh $a;
        close($fh);
    }
}

print "Done\n";
