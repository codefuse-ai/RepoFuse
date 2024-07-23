require_relative 'helper'

class AnotherHelper
  def initialize
    Helper.greet
  end

  def some_method
    puts "This is an example method from AnotherHelper class."
  end
end
