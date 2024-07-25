require_relative 'lib/helper'
require_relative 'lib/another_helper'
require 'greeting'

greet
another_helper = AnotherHelper.new
another_helper.some_method
Helper.greet
