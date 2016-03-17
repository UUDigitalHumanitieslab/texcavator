// FL-21-Feb-2012 Created
// FL-13-Jun-2013 Changed

// startsWith to check if a string starts with a particular character sequence
String.prototype.startsWith = function( str )
{ return( this.match( "^" + str ) == str ); };

// endsWith to check if a string ends with a particular character sequence:
String.prototype.endsWith = function( str )
{ return( this.match( str + "$" ) == str ); };

function isWhitespaceOrEmpty( text ) {
   return !/[^\s]/.test( text );
}