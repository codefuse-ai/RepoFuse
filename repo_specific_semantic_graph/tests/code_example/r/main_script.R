# main_script.R

# Use source() to import external_script.R
source("external_script.R")

# Now we can use the function and variable defined in external_script.R
result <- add_numbers(5, 10)
print(result)  # 15

print(some_value)  # 42
