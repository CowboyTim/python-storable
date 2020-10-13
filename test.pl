#!/usr/bin/perl

use lib 'perl-modules';
use strict; use warnings;

use FindBin;
use lib "$FindBin::Bin";

use Fcntl ":seek";
use Fatal qw(open);
use File::Path qw(mkpath);
use Config;
use Encode qw(_utf8_on);

use Storable qw(nfreeze freeze nstore store);

# make the base path
my $base = 
    "$FindBin::Bin/tests/resources/$Config{myarchname}/$Storable::VERSION";
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
    # that this is a reference SX_OBJECT test allready too
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
    # same thing with an array of course. The 'a', 'b', 'c' appear to be tied
    # scalars in a storable too.
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

{
    # same but try to make 'a', 'b', 'c' not tied scalars
    my $a = [undef, 6, ['a', 'b', 'c', {'uu' => 5.6}]];
    $a->[6] = \$a->[0];
    $a->[7] = \$a->[1];
    $a->[5] =  $a->[2];
    $a->[4] =  $a->[2][3];
    $a->[3] =  $a->[2][3];
    save_sample('complex08', $a);
}

{
    # bless test: scalar, $test is undef => will result in 'None'
    my $a = bless \my $test, 'Aa::Bb';
    save_sample('bless01', $a);
}

{
    # bless test: scalar, $test is 'Test' => will result in 'Test'
    my $test = 'Test';
    my $a = bless \$test, 'Aa::Bb';
    save_sample('bless02', $a);
}

{
    # bless test: array
    my $a = bless [], 'Aa::Bb';
    save_sample('bless03', $a);
}

{
    # bless test: hash
    my $a = bless {}, 'Aa::Bb';
    save_sample('bless04', $a);
}

{
    # bless test: ref to a ref
    my $a = bless \{}, 'Aa::Bb';
    save_sample('bless05', $a);
}

{
    # bless test: more than one bless, all the same one though
    my $a = bless [
        bless({}, 'Aa::Bb'),
        bless([], 'Aa::Bb'),
        bless(\[], 'Aa::Bb'),
        bless(\my $test1, 'Aa::Bb'),
        bless(\my $test2, 'Aa::Cc'),
        bless(['TestA'], 'Aa::Cc'),
        bless(['TestB'], 'Aa::Dd'),
        bless(['TestC'], 'Aa::Cc'),
        bless(['TestD', bless({0=>bless([], 'Aa::Bb')}, 'Aa::Cc')], 'Aa::Bb'),
    ], 'Aa::Bb';
    save_sample('bless06', $a);
}

{
    # bless test: bless without a package
    my $a = bless [];
    save_sample('bless07', $a);
}

{
    # utf-8 test
    my $a = "\x{263A}";
    save_sample('utf8test01', \$a);
}

{
    # utf-8 test: large scalar
    my $a = "\x{263A}" x 1024;
    save_sample('utf8test02', \$a);
}

{
    # SX_HOOK test: simple array-return
    package Test;
    sub new {bless {-test => [], -testscalar => 'Hello world'}, $_[0]};
    sub STORABLE_freeze {
        return 1, $_[0]->{-test}, \$_[0]->{-testscalar};
    }

    package main;
    
    my $h = Test->new();
    save_sample('medium_complex_hook_test', $h);
}

{
    # SX_HOOK test: large simple array-return
    package Test2;
    sub new {bless {}, $_[0]};
    sub STORABLE_freeze {
        return 0, map {\$_[0]->{$_}} (('x') x 300);
    }

    package main;
    
    my $h = Test2->new();
    save_sample('medium_complex_hook_test_large_array', $h);
}

{
    # SX_HOOK test: multiple test: same scalar
    package Test3;
    sub new {bless {}, $_[0]};
    sub STORABLE_freeze {
        return 0, \'some scalar var';
    }

    package main;
    
    my $a = [ Test3->new(), Test3->new() ];
    save_sample('medium_complex_multiple_hook_test', $a);
}

{
    # SX_HOOK test: multiple test: different scalar
    package Test4;
    sub new {bless {-v => $_[1]}, $_[0]};
    sub STORABLE_freeze {
        return 0, \$_[0]->{-v};
    }

    package main;
    
    my $a = [ Test4->new('var 1'), Test4->new('var 2') ];
    save_sample('medium_complex_multiple_hook_test2', $a);
}

{
    # SX_HOOK test: array
    package Test6;
    sub new {bless [$_[1]], $_[0]};
    sub STORABLE_freeze {
        return 0, \$_[0][0];
    }

    package main;
    
    my $a = [ Test6->new('avar 1'), Test6->new('avar 2') ];
    save_sample('medium_hook_array_test1', $a);
}

{
    # SX_HOOK test: multiple test: own serialized + array
    package Test7;
    sub new {bless [$_[1]], $_[0]};
    sub STORABLE_freeze {
        return "SERIALIZED:$_[0]->[0]:SERIALIZED", \$_[0][0];
    }

    package main;

    my $a = [ Test7->new('svar 1'), Test7->new('svar 2') ];
    save_sample('medium_own_serialized1', $a);
}

{
    # SX_HOOK test: test: scalar
    package Test8;
    sub new {bless \(my $_dummy = $_[1]), $_[0]};
    sub STORABLE_freeze {
        return 0, $_[0], \10, \'Test string';
    }

    package main;

    my $a = Test8->new('scalar var 1');
    save_sample('medium_hook_scalar', $a);
}

{
    # SX_HOOK test: test: scalar, large serialize string
    package Test9;
    sub new {bless \(my $_dummy = $_[1]), $_[0]};
    sub STORABLE_freeze {
        return 'x'x300, $_[0], \10, \'Test string';
    }

    package main;

    my $a = Test9->new('large scalar var 1');
    save_sample('large_frozen_string_hook', $a);
}

{
    # SX_HOOK test: array
    package Test10;
    sub new {bless [$_[1]], $_[0]};
    sub STORABLE_freeze {
        return 0, \$_[0][0];
    }

    package main;
    
    my $b = Test10->new('scalar var 1');
    my $a = [ 
        $b,
        Test10->new('scalar var 2'), 
        Test10->new('scalar var 3'),
        $b
    ];
    save_sample('medium_hook_array_three', $a);
}

{
    save_sample('integer',    \44556677);
}

{
    save_sample('biginteger', \112233445566778899);
}

{
    save_sample('integer_array', [44556677, 556677]);
}

{
    save_sample('integer_hash',  {44556677 => 'a', 556677 => 'b'});
}

{
    # Immortal test: undef
    save_sample('immortal_test01_undef', \undef());
}

{
    # Immortal test: yes
    save_sample('immortal_test02_yes', \!0);
}

{
    # Immortal test: no
    #save_sample('immortal_test03_no', \!1);
    # This _would_ work if !1 wasn't a dualvar... :|
    # Was dualvar added after PL_sv_(yes|no)?
    # How do i get an instance of PL_sv_no that isn't a dualvar such that
    # storable will write it and not the scalar?
    # For now, write out something of the same expected length, then modify it
    # to what it should be.
    my @names = save_sample('immortal_test03_no', \!0);
    my $sx_sv_no = "\x{10}";
    for my $filename (@names) {
        open(my $fh, '+<:raw', $filename) or die;
        seek($fh, -1, SEEK_END);
        print $fh $sx_sv_no;
        close $fh;
    }
}

{
    # Version test (short)
    my $a = v5.6.0.0.35;
    save_sample('version_test01_short', \$a);
}

{
    # Version test (long)
    my $a = v5.6.0.0.35555555555.5555555555.555555555.555555555.555555555.5555555555.5555555555.5555555.555555555.55555555.555555555.55555555.555555555.555555555.555555555.5555555555.5555555555.5555555.555555555.33333333.333333333.33333333.333333333.333333333.333333333.1111111111;
    save_sample('version_test02_long', \$a);
}

{
    # utf-8 test: small scalar, but looks like a float, or set utf-8 on a string that does that
    my $a = "0.1334e-6";
    _utf8_on($a);
    save_sample('utf8test03', \$a);
}

sub save_sample {
    my ($what, $data) = @_;
    $count++;
    my @filenames = ();
    for my $type (qw(freeze nfreeze)){
        my $filename = generate_filename($what, $count, $type);
        push @filenames, $filename;
        my $a;
        {
            no strict 'refs';
            $a = &$type($data);
        }
        open(my $fh, '>', $filename);
        print $fh $a;
        close($fh);
    }

    for my $type (qw(store nstore)){
        my $filename = generate_filename($what, $count, $type);
        push @filenames, $filename;
        my $a;
        {
            no strict 'refs';
            $a = &$type($data, $filename);
        }
    }
    return @filenames;
}

sub generate_filename {
    my ($what, $count, $type) = @_;
    my $filename =
        "$base/".sprintf('%03d', $count)."_${what}_".
        "${Storable::VERSION}_$Config{myarchname}_${type}.storable";

    print "saving sample $what for $type to $filename\n";
    die "Duplicate filename $filename\n"
        if exists $filenames->{$filename};
    $filenames->{$filename} = 1;
    return $filename;
}

print "Done\n";
