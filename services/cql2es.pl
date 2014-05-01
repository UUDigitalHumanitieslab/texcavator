#!/usr/bin/perl

=for comment
"""
--------------------------------------------------------------------------------
Author:		Fons Laan, ILPS-ISLA, University of Amsterdam
Project:	BiLand
Name:		cql2es.pl
Version:	0.1
Goal:		Convert a CQL query to an ElasticSearch query
Notice:		When running this script directly for debug purposes some env vars must be set,
			depending on your installation, something like this: 
				$ export PERLBREW_ROOT=/datastore/aclaan/perl5/perlbrew
				$ export PERLBREW_HOME=/datastore/aclaan/perl5/.perlbrew
				$ $PERLBREW_ROOT/bin/perlbrew switch perl-5.10.1

FL-13-Feb-2013: Created
FL-26-Aug-2013: Changed
=cut

use strict;
use warnings;

use Data::Dumper;
use Module::Load;
use JSON::XS;
use Catmandu::Store::ElasticSearch::CQL;
use MIME::Base64;
use Encode qw(decode);		# FL: UTF-8 needed for query strings with trema's...

my $debug = 0;
#if( $debug ) { print STDERR "cql2es.pl\n"; }

# process command line arguments
my $num_args = $#ARGV + 1;
#print STDERR $num_args, "\n";
#foreach my $arg (@ARGV) {
#	print STDERR $arg, "\n";
#}

my $cql_query_string = "";
if( $debug ) { print STDERR "num_args: $num_args\n"; }

#my $encoded = "S2VsbG9nZyBBTkQgcGFwZXJfZGNfZGF0ZSA8PSAxOTQ1MTIzMQ==";
#print STDERR "encoded: ", $encoded, "\n";
#my $decoded = decode_base64( $encoded );
#print STDERR "decoded: ", $decoded, "\n";


if( $num_args eq 3 ) {
	if( $debug ) { print STDERR $ARGV[ 0 ], "\n" }
	if( $debug ) { print STDERR $ARGV[ 1 ], "\n" }
	if( $debug ) { print STDERR $ARGV[ 2 ], "\n" }
}

if( $num_args eq 2 ) {
	if( $debug ) { print STDERR "0: ", $ARGV[ 0 ], "\n"; }
	if( $debug ) { print STDERR "1: ", $ARGV[ 1 ], "\n"; }

	my $encoded_base64 = $ARGV[ 1 ];
	my $decoded_base64 = decode_base64( $encoded_base64 );
	print STDERR "decoded_base64: ", $decoded_base64, "\n";

	# base64 decoded, but still need to deal with utf8 chars in query
	my $decoded_utf8 = decode( 'UTF-8', $decoded_base64 );

	print STDERR "decoded_utf8: ", $decoded_base64, "\n";

#	print STDERR $ARGV[ 0 ], "\n";
	if( $ARGV[ 0 ] eq "-q" || $ARGV[ 0 ] eq "--query" ) {
	#	print STDERR $ARGV[ 1 ], "\n";
	#	$cql_query_string = $ARGV[ 1 ];

		$cql_query_string = $decoded_utf8;
		if( $debug ) { print STDERR $cql_query_string, "\n"; }
		if( $cql_query_string eq "" ) {
			print STDERR "";
			exit 0;
		}
	}
	else {
		exit 0;
	}
}
else {
	exit 0;
}
if( $debug ) { print STDERR "CQL: |$cql_query_string|\n"; }

#$cql_query_string = "\"" . "\\" . $cql_query_string . "\\";
#$cql_query_string = "\\"watervliegtuig in\\"";
#$cql_query_string = "Kellogg's AND paper_dc_date <= 19451231";
#if( $debug ) { print STDERR "CQL: |$cql_query_string|\n"; }



=for comment
my $cql_query_string = "opium";
my $cql_query_string = "opium AND dc.date <= 19451231";
my $cql_query_string = "opium AND (dc.date <= 19451231 AND dc.date >= 19451231)";
startRecord=1&
x-collection=DDD_artikel&
recordSchema=ddd
=cut

my $cql_mapping;
my $es_query = Catmandu::Store::ElasticSearch::CQL
	->new( mapping => $cql_mapping )
	->parse( $cql_query_string );

#print STDERR Dumper( $es_query );		# $es_query is a HASH

my $json_text = encode_json( $es_query );
if( $debug ) { print STDERR "JSON: |$json_text|\n"; }

print $json_text;	# 'return', DO NOT PRINT TO STDERR

#my $json = new JSON;
#print STDERR $json->utf8->pretty->encode( $es_query );


# [eof]
