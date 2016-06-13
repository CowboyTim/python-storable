use Storable;

my $list = [1, 'one', 1.5, [1, 2, 3], {name => 'Quasar'}];
my $simple = 'test';

store \$simple, 'test.pinfo';
