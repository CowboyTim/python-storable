use Storable;
use Data::Dumper;

my $data = retrieve 'storetest.pinfo';
print ref($data), "\n";
print Dumper($data);

