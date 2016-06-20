use Storable;

my $list = [1, undef, 1.5, '1.6', [1, 2, 3], {name => 'Quasar'}];
my $simple = 'test';

store $list, 'test.pinfo';
