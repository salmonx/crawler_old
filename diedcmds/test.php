<?php

$pass = "CZLczl12123";
$salt = "27d2e5";
echo md5(md5($pass).$salt);
