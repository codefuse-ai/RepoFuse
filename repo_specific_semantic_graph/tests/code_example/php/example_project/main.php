<?php
require_once 'helpers/config.php';

include 'helpers/functions.php';

require 'helpers/constants.php';

require 'helpers/constants.php';

require './greeting.php';

// 使用这些资源
echo SITE_NAME . PHP_EOL;
sayHello('John Doe');
greeting('John Doe');
echo $config['database']['host'] . PHP_EOL;
