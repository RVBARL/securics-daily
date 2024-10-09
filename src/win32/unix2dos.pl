#!/usr/bin/perl
# Copyright (C) 2023-2024, RV Bionics Group SpA.

my $file;

if(@ARGV < 1)
{
    die "$0: <file>\n";
}

$file = shift (@ARGV);

# File
open(FILE,"<$file")|| die "Unable to open file: $file\n";

while(<FILE>)
{
    my $line = $_;

    $line =~ s/\n/\r\n/;
    print $line;
}
