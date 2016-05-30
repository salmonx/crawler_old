<?php
##########################################################################
#	
#	AZ Environment variables 1.04 © 2004 AZ
#	Civil Liberties Advocacy Network
#	http://clan.cyaccess.com   http://clanforum.cyaccess.com
#	
#	AZenv is written in PHP & Perl. It is coded to be simple,
#	fast and have negligible load on the server.
#	AZenv is primarily aimed for programs using external scripts to
#	verify the passed Environment variables.
#	Only the absolutely necessary parameters are included.
#	AZenv is free software; you can use and redistribute it freely.
#	Please do not remove the copyright information.
#
##########################################################################

foreach ($_SERVER as $header => $value )
{ if 	(strpos($header , 'REMOTE')!== false || strpos($header , 'HTTP')!== false ||
	strpos($header , 'REQUEST')!== false) {echo $header.' = '.$value."\n"; } }
?>
