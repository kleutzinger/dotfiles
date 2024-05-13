#!/usr/bin/perl

# filters a list of files to only those that exist
# usage: ls | exists.pl
# output: list of files that exists

use strict;

while (<>) {
    chomp;
    if (-e $_) {
        print "$_\n";
    }
}
chomp(); if (-e $_) {print "$_\n"}
