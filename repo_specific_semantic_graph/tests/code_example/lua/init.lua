-- Load module1.lua
local module1 = require('module1')

-- Load module2.lua from submodule directory
local module2 = require("submodule.module2")

require("module3")

dofile("module4.lua")

-- Use the functions from the modules
module1.greet()
module2.greet()
