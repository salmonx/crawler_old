<?php

if (isset($_POST['username'])){
	$u = $_POST['username'];
	$p = $_POST['password'];
	if ($u == 'admin' && $p == 'abcd1234'){
		echo "success";
	}
	else 	echo "failed";
}
?>

<html>
<body>
<form method = post>
	<input type=text name=username>
	<input type=password name=password>
	<input type=submit>
</form>
</body>
</html>
