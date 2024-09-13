mod my_module;
mod my_other_module;
mod foo;

use my_module::sub_module::sub_function;
use my_other_module::helper::helper_function;
// At crate root
use crate::foo::foo;

use my_module::bar::bar_function as bar;

fn main() {
    sub_function();
    helper_function();
    foo();

    // Using a utility function from utils.rs
    my_module::utils::utility_function();
    bar();
}
